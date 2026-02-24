import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# --- Path setup so we can import shared core + app_state ---
BASE = Path(__file__).resolve().parents[2]  # .../apps/debt_calculator
sys.path.insert(0, str(BASE / "shared"))
sys.path.insert(0, str(BASE / "web"))  # so we can import app_state.py

from app_state import (
    get_active_profile, list_profiles, set_active_profile,
    add_profile, rename_profile, delete_profile,
    load_section, save_section
)

st.set_page_config(page_title="Bills • Debt Calculator", page_icon="🧾", layout="wide")

st.title("Bills")
st.caption("Add, edit, and manage bills for the selected profile (persistent storage).")

# -----------------------------
# Persistence helpers
# -----------------------------
def load_bills() -> list[dict]:
    payload = load_section("bills")
    return (payload or {}).get("items", []) or []

def save_bills(items: list[dict]) -> None:
    save_section("bills", {"items": items})

# -----------------------------
# Profile controls
# -----------------------------
profiles_list = list_profiles()
active = get_active_profile()

name_to_id = {p.name: p.id for p in profiles_list}
names = [p.name for p in profiles_list]
current_index = names.index(active.name) if active.name in names else 0

st.subheader("Profile")

colp1, colp2, colp3, colp4 = st.columns([2, 1, 1, 1])

with colp1:
    selected_name = st.selectbox("Active profile", names, index=current_index)
    selected_id = name_to_id[selected_name]
    if selected_id != active.id:
        set_active_profile(selected_id)
        # reset cached bills for new profile
        st.session_state.pop("bills_cache", None)
        st.rerun()

with colp2:
    new_name = st.text_input("New profile name", value="", placeholder="e.g., Household")
    if st.button("Add Profile"):
        add_profile((new_name or "New Profile").strip())
        st.session_state.pop("bills_cache", None)
        st.rerun()

with colp3:
    rename_to = st.text_input("Rename active to", value="", placeholder="New name")
    if st.button("Rename"):
        rename_profile(active.id, (rename_to or active.name).strip())
        st.rerun()

with colp4:
    if st.button("Delete Active"):
        try:
            delete_profile(active.id)
            st.session_state.pop("bills_cache", None)
            st.rerun()
        except Exception as e:
            st.error(str(e))

st.divider()

# -----------------------------
# Load bills once per profile (cache in session_state)
# -----------------------------
if "bills_cache" not in st.session_state:
    st.session_state["bills_cache"] = load_bills()

bills = st.session_state["bills_cache"]

# -----------------------------
# Add Bill form
# -----------------------------
st.markdown("### Add a bill")

with st.form("add_bill_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Bill name *")
        amount = st.number_input("Balance/Amount *", min_value=0.0, step=10.0, format="%.2f")
    with c2:
        due_day = st.number_input("Due day (1-31)", min_value=1, max_value=31, value=1)
        apr = st.number_input("APR % (optional)", min_value=0.0, step=0.25, format="%.2f")
    with c3:
        min_payment = st.number_input("Min payment (optional)", min_value=0.0, step=10.0, format="%.2f")
        notes = st.text_input("Notes (optional)")

    submitted = st.form_submit_button("Add bill")
    if submitted:
        if not name.strip():
            st.error("Bill name is required.")
        elif amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            bills.append(
                {
                    "name": name.strip(),
                    "amount": float(amount),
                    "due_day": int(due_day),
                    "apr": float(apr),
                    "min_payment": float(min_payment),
                    "notes": notes.strip(),
                }
            )
            save_bills(bills)
            st.success("Bill added.")
            st.rerun()

st.divider()

# --- Payoff fields ---
include_in_strategy = st.checkbox("Include in payoff strategy", value=True)
planned_payment = st.number_input("Planned payment (optional)", min_value=0.0, step=10.0, format="%.2f")
status = st.selectbox("Status", ["Current", "Delinquent", "Collections", "Paid"], index=0)

override_mode = st.selectbox("Override (optional)", ["None", "Payment", "Target Months"], index=0)
override_value = 0.0
override_months = 0
if override_mode == "Payment":
    override_value = st.number_input("Override payment", min_value=0.0, step=10.0, format="%.2f")
elif override_mode == "Target Months":
    override_months = st.number_input("Target months", min_value=1, max_value=600, value=12)


# -----------------------------
# Bills table + edit/delete
# -----------------------------
st.markdown("### Current bills")

if not bills:
    st.info("No bills yet. Add one above.")
    st.stop()

df = pd.DataFrame(bills)
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("#### Edit / Delete")

idx = st.number_input(
    "Select bill # (row index)",
    min_value=0,
    max_value=len(bills) - 1,
    value=0
)

selected = bills[int(idx)]

with st.form("edit_bill_form"):
    e1, e2, e3 = st.columns(3)

    with e1:
        ename = st.text_input("Bill name", value=selected.get("name", ""))
        eamount = st.number_input(
            "Balance/Amount",
            min_value=0.0,
            step=10.0,
            value=float(selected.get("amount", 0.0)),
            format="%.2f",
        )
        einclude = st.checkbox(
            "Include in payoff strategy",
            value=bool(selected.get("include_in_strategy", True)),
        )

    with e2:
        edue = st.number_input(
            "Due day",
            min_value=1,
            max_value=31,
            value=int(selected.get("due_day", 1)),
        )
        eapr = st.number_input(
            "APR %",
            min_value=0.0,
            step=0.25,
            value=float(selected.get("apr", 0.0)),
            format="%.2f",
        )
        estatus = st.selectbox(
            "Status",
            ["Current", "Delinquent", "Collections", "Paid"],
            index=["Current", "Delinquent", "Collections", "Paid"].index(
                selected.get("status", "Current") if selected.get("status", "Current") in ["Current", "Delinquent", "Collections", "Paid"] else "Current"
            ),
        )

    with e3:
        emin = st.number_input(
            "Min payment",
            min_value=0.0,
            step=10.0,
            value=float(selected.get("min_payment", 0.0)),
            format="%.2f",
        )
        eplanned = st.number_input(
            "Planned payment",
            min_value=0.0,
            step=10.0,
            value=float(selected.get("planned_payment", selected.get("min_payment", 0.0) or 0.0)),
            format="%.2f",
        )
        enotes = st.text_input("Notes", value=selected.get("notes", ""))

    st.divider()
    st.markdown("#### Overrides (optional)")

    # Determine current override
    cur_override = selected.get("override", {}) or {}
    cur_mode = "None"
    cur_payment = 0.0
    cur_months = 12

    if isinstance(cur_override, dict):
        if "payment" in cur_override:
            cur_mode = "Payment"
            cur_payment = float(cur_override.get("payment") or 0.0)
        elif "target_months" in cur_override:
            cur_mode = "Target Months"
            cur_months = int(cur_override.get("target_months") or 12)

    o1, o2, o3 = st.columns([1.2, 1, 1])
    with o1:
        override_mode = st.selectbox(
            "Override mode",
            ["None", "Payment", "Target Months"],
            index=["None", "Payment", "Target Months"].index(cur_mode),
        )
    with o2:
        override_payment = st.number_input(
            "Override payment",
            min_value=0.0,
            step=10.0,
            value=cur_payment,
            format="%.2f",
            disabled=(override_mode != "Payment"),
        )
    with o3:
        override_months = st.number_input(
            "Target months",
            min_value=1,
            max_value=600,
            value=cur_months,
            disabled=(override_mode != "Target Months"),
        )

    st.divider()
    st.markdown("#### Custom strategy order (only used if Strategy = Custom)")
    custom_order = st.number_input(
        "Custom order (lower = earlier payoff target)",
        min_value=1,
        max_value=999999,
        value=int(selected.get("custom_order", 999999) or 999999),
    )

    csave, cdel = st.columns([1, 1])
    save_clicked = csave.form_submit_button("Save changes")
    delete_clicked = cdel.form_submit_button("Delete bill")

    if save_clicked:
        # Build override dict
        override = {}
        if override_mode == "Payment":
            override = {"payment": float(override_payment)}
        elif override_mode == "Target Months":
            override = {"target_months": int(override_months)}

        bills[int(idx)] = {
            "name": ename.strip(),
            "amount": float(eamount),
            "due_day": int(edue),
            "apr": float(eapr),
            "min_payment": float(emin),
            "planned_payment": float(eplanned) if eplanned > 0 else float(emin),
            "include_in_strategy": bool(einclude),
            "status": estatus,
            "override": override,
            "custom_order": int(custom_order),
            "notes": enotes.strip(),
        }

        save_bills(bills)
        st.success("Saved.")
        st.rerun()

    if delete_clicked:
        bills.pop(int(idx))
        save_bills(bills)
        st.success("Deleted.")
        st.rerun()

# --- Payoff fields ---
include_in_strategy = st.checkbox("Include in payoff strategy", value=True)
planned_payment = st.number_input("Planned payment (optional)", min_value=0.0, step=10.0, format="%.2f")
status = st.selectbox("Status", ["Current", "Delinquent", "Collections", "Paid"], index=0)

override_mode = st.selectbox("Override (optional)", ["None", "Payment", "Target Months"], index=0)
override_value = 0.0
override_months = 0
if override_mode == "Payment":
    override_value = st.number_input("Override payment", min_value=0.0, step=10.0, format="%.2f")
elif override_mode == "Target Months":
    override_months = st.number_input("Target months", min_value=1, max_value=600, value=12)
