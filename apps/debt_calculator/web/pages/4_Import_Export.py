import streamlit as st
import sys
from pathlib import Path
import json
import pandas as pd

# --- Path setup so we can import app_state ---
BASE = Path(__file__).resolve().parents[2]  # .../apps/debt_calculator
sys.path.insert(0, str(BASE / "web"))

from app_state import get_active_profile, load_section, save_section

st.set_page_config(page_title="Import/Export • Debt Calculator", page_icon="📦", layout="wide")

st.title("Import / Export")
st.caption("Export or import your bills for the active profile (JSON now; Excel next).")

active = get_active_profile()

st.markdown(f"### Active profile: **{active.name}**")
st.divider()

# Load current bills
bills_payload = load_section("bills")
bills = (bills_payload or {}).get("items", []) or []

# -----------------------------
# EXPORT
# -----------------------------
st.markdown("## Export")

c1, c2 = st.columns([1, 1.5])

with c1:
    st.write("**Export as JSON** (recommended backup)")
    export_obj = {
        "profile": {"id": active.id, "name": active.name},
        "bills": bills,
    }
    export_json = json.dumps(export_obj, indent=2)

    st.download_button(
        label="Download JSON",
        data=export_json,
        file_name=f"debt_calculator_{active.name.replace(' ', '_').lower()}_bills.json",
        mime="application/json",
    )

with c2:
    st.write("**Preview (table)**")
    if bills:
        st.dataframe(pd.DataFrame(bills), use_container_width=True, hide_index=True)
    else:
        st.info("No bills to export yet.")

st.divider()

# -----------------------------
# IMPORT
# -----------------------------
st.markdown("## Import")

st.warning(
    "Import will replace the current bills list for this profile. "
    "Download an export first if you want a backup."
)

uploaded = st.file_uploader("Upload JSON export", type=["json"])

if uploaded:
    try:
        raw = uploaded.read().decode("utf-8")
        obj = json.loads(raw)

        incoming_bills = obj.get("bills", [])
        if not isinstance(incoming_bills, list):
            raise ValueError("Invalid JSON: 'bills' must be a list.")

        # Minimal validation + normalization
        cleaned = []
        for b in incoming_bills:
            if not isinstance(b, dict):
                continue
            name = str(b.get("name", "")).strip()
            amount = float(b.get("amount", 0.0) or 0.0)
            if not name or amount <= 0:
                continue

            cleaned.append(
                {
                    "name": name,
                    "amount": amount,
                    "due_day": int(b.get("due_day", 1) or 1),
                    "apr": float(b.get("apr", 0.0) or 0.0),
                    "min_payment": float(b.get("min_payment", 0.0) or 0.0),
                    "notes": str(b.get("notes", "") or "").strip(),
                }
            )

        st.success(f"Parsed {len(cleaned)} bills from import.")
        st.dataframe(pd.DataFrame(cleaned), use_container_width=True, hide_index=True)

        colA, colB = st.columns(2)
        with colA:
            if st.button("Replace current bills with import"):
                save_section("bills", {"items": cleaned})
                st.success("Import complete. Bills replaced for this profile.")
                st.rerun()

        with colB:
            st.caption("Tip: Use Import when moving data between computers/profiles.")

    except Exception as e:
        st.error(f"Import failed: {e}")
