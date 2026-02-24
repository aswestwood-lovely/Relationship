from __future__ import annotations
import base64, hmac, hashlib
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Tuple, Optional
import streamlit as st

from .storage import load_json, save_json, ensure_dir

LICENSE_SECRET = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
LICENSE_PATH = Path(__file__).resolve().parent.parent / "saves" / "license.json"

def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64u_decode(s: str) -> bytes:
    pad = "=" * ((4 - (len(s) % 4)) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("utf-8"))

def sign_payload(payload_b64: str) -> str:
    sig = hmac.new(LICENSE_SECRET.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    return _b64u(sig)[:22]

def make_key(payload: Dict[str, Any]) -> str:
    import json
    payload_b64 = _b64u(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    sig = sign_payload(payload_b64)
    return f"DC1-{payload_b64}-{sig}"

def parse_and_validate_key(key: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    import json
    key = (key or "").strip()
    if not key.startswith("DC1-"):
        return False, "Invalid key format.", None
    parts = key.split("-")
    if len(parts) < 3:
        return False, "Invalid key format.", None
    payload_b64 = parts[1]
    sig = parts[2]
    expected = sign_payload(payload_b64)
    if not hmac.compare_digest(sig, expected):
        return False, "Key signature is invalid.", None
    try:
        payload = json.loads(_b64u_decode(payload_b64).decode("utf-8"))
    except Exception:
        return False, "Key payload could not be read.", None

    ktype = payload.get("type", "full")
    if ktype not in ("full","trial"):
        return False, "Unknown key type.", None
    exp = payload.get("exp")
    if exp:
        try:
            y,m,d = [int(x) for x in exp.split("-")]
            exp_date = date(y,m,d)
            if date.today() > exp_date:
                return False, f"Key expired on {exp_date.isoformat()}.", None
        except Exception:
            return False, "Key expiry is invalid.", None
    return True, "Key is valid.", payload

def _load_license_state() -> Dict[str, Any]:
    return load_json(LICENSE_PATH, default={
        "activated": False,
        "license_key": "",
        "license_type": "",
        "activated_on": "",
        "trial_started_on": "",
        "trial_days": 14,
        "last_ok": "",
        "licensed_to": "",
    })

def _save_license_state(state: Dict[str, Any]) -> None:
    ensure_dir(LICENSE_PATH.parent)
    save_json(LICENSE_PATH, state)

def is_unlocked() -> Tuple[bool, str]:
    state = _load_license_state()
    if state.get("activated") and state.get("license_type") == "full":
        ok, _, _ = parse_and_validate_key(state.get("license_key",""))
        if ok:
            return True, "Activated"
        return False, "Stored license key is no longer valid."

    if state.get("license_type") == "trial" and state.get("trial_started_on"):
        try:
            y,m,d = [int(x) for x in state["trial_started_on"].split("-")]
            start = date(y,m,d)
            days = int(state.get("trial_days", 14))
            if date.today() <= start + timedelta(days=days-1):
                return True, f"Trial active (day {(date.today()-start).days+1} of {days})"
            return False, "Trial period ended."
        except Exception:
            return False, "Trial state is corrupted."

    return False, "Not activated."

def render_gate(app_title: str = "Debt Calculator") -> None:
    unlocked, status = is_unlocked()
    if unlocked:
        st.session_state["license_status"] = status
        return

    st.set_page_config(page_title=f"{app_title} - Locked", layout="wide")
    st.title("🔒 Application Locked")
    st.write("Enter a license key to unlock the application, or activate a 14-day trial using a trial key.")

    state = _load_license_state()
    with st.form("license_form", clear_on_submit=False):
        key = st.text_input("License key / Trial key", value="", placeholder="DC1-...-...")
        name = st.text_input("Licensed to (optional)", value=state.get("licensed_to",""))
        submitted = st.form_submit_button("Unlock")

    if submitted:
        ok, msg, payload = parse_and_validate_key(key)
        if not ok:
            st.error(msg)
        else:
            ktype = payload.get("type", "full")
            today = date.today().isoformat()
            new_state = dict(state)
            new_state["license_key"] = key.strip()
            new_state["license_type"] = ktype
            new_state["licensed_to"] = name.strip()
            new_state["last_ok"] = today
            if ktype == "full":
                new_state["activated"] = True
                new_state["activated_on"] = today
                new_state["trial_started_on"] = ""
                _save_license_state(new_state)
                st.success("Unlocked with full license. Please refresh.")
                st.stop()
            else:
                new_state["activated"] = False
                new_state["trial_started_on"] = today
                new_state["trial_days"] = 14
                _save_license_state(new_state)
                st.success("Trial activated for 14 days. Please refresh.")
                st.stop()

    st.info("Tip: The project includes keygen.py to generate full and trial keys.")
    st.stop()
