import streamlit as st
import sys
from pathlib import Path
from datetime import date
import pandas as pd

# --- Path setup so we can import shared core + app_state ---
BASE = Path(__file__).resolve().parents[2]  # .../apps/debt_calculator
sys.path.insert(0, str(BASE / "shared"))
sys.path.insert(0, str(BASE / "web"))

from app_state import get_active_profile, load_section
import core.payoff as payoff  # monthly_plan, strategy_order, amortize

st.set_page_config(page_title="Payoff Plan • Debt Calculator", page_icon="🏁", layout="wide")

st.title("Payoff Plan")
st.caption("Generate a monthly plan using Avalanche/Snowball/Custom and see payoff projections.")

active = get_active_profile()
bills_payload = load_section("bills")
bills = (bills_payload or {}).get("items", []) or []

# -----------------------------
# Convert bills -> debts format expected by payoff.py
# -----------------------------
def bills_to_debts(bills_list):
    debts = []
    for i, b in enumerate(bills_list):
        debts.append(
            {
                "id": b.get("id", i),
                "name": b.get("name", f"Debt {i+1}"),
                "balance": float(b.get("amount", 0.0) or 0.0),
                "apr": float(b.get("apr", 0.0) or 0.0),
                "min_payment": float(b.get("min_payment", 0.0) or 0.0),
                "planned_payment": float(b.get("planned_payment", b.get("min_payment", 0.0) or 0.0) or 0.0),
                "include_in_strategy": bool(b.get("include_in_strategy", True)),
                "override": b.get("override", {}) or {},
                "status": b.get("status", "Current"),
                "custom_order": int(b.get("custom_order", 999999) or 999999),
            }
        )
    return debts

debts = bills_to_debts(bills)

# -----------------------------
# Controls
# -----------------------------
c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])

with c1:
    strategy = st.selectbox("Strategy", ["Avalanche", "Snowball", "Custom"], index=0)

with c2:
    extra_payment = st.number_input("Extra monthly payment", min_value=0.0, step=25.0, format="%.2f", value=0.0)

with c3:
    status_override = st.checkbox("Status override priority", value=True)

with c4:
    start = st.date_input("Start date", value=date.today())

st.divider()

if not debts:
    st.info("No debts found. Add bills in the **Bills** page first.")
    st.stop()

# -----------------------------
# Included debts preview
# -----------------------------
st.markdown("### Included debts")
inc_df = pd.DataFrame(
    [
        {
            "name": d["name"],
            "balance": d["balance"],
            "apr": d["apr"],
            "min_payment": d["min_payment"],
            "include": d["include_in_strategy"],
        }
        for d in debts
    ]
)
st.dataframe(inc_df, use_container_width=True, hide_index=True)

st.caption("Next improvement: add include/exclude toggles and overrides directly on this page.")

st.divider()

# -----------------------------
# Generate plan
# -----------------------------
plan_rows = payoff.monthly_plan(
    debts=debts,
    strategy=strategy,
    extra_payment=float(extra_payment),
    status_override=bool(status_override),
)

st.markdown("### Monthly Plan (payments)")
plan_df = pd.DataFrame(plan_rows)
st.dataframe(plan_df, use_container_width=True, hide_index=True)

required_total = float(plan_df.loc[plan_df["kind"] == "required", "payment"].sum()) if not plan_df.empty else 0.0
extra_total = float(plan_df.loc[plan_df["kind"] == "extra", "payment"].sum()) if not plan_df.empty else 0.0

m1, m2, m3 = st.columns(3)
m1.metric("Required monthly total", f"${required_total:,.2f}")
m2.metric("Extra allocated", f"${extra_total:,.2f}")
m3.metric("All-in monthly total", f"${(required_total + extra_total):,.2f}")

st.divider()

# -----------------------------
# Order preview
# -----------------------------
st.markdown("### Strategy Order (preview)")
ordered = payoff.strategy_order(debts, strategy=strategy, status_override=bool(status_override))
order_df = pd.DataFrame(
    [
        {
            "order": i + 1,
            "name": d["name"],
            "balance": d["balance"],
            "apr": d["apr"],
            "status": d.get("status", "Current"),
        }
        for i, d in enumerate(ordered)
    ]
)
st.dataframe(order_df, use_container_width=True, hide_index=True)

st.divider()

# -----------------------------
# Payoff projection for a selected debt (using amortize)
# -----------------------------
st.markdown("### Payoff projection (single debt)")
debt_names = [d["name"] for d in debts]
selected_name = st.selectbox("Select debt to project", debt_names, index=0)

selected_debt = next(d for d in debts if d["name"] == selected_name)

planned_payment = float(plan_df.loc[plan_df["name"] == selected_name, "payment"].sum()) if not plan_df.empty else selected_debt["min_payment"]

try:
    result = payoff.amortize(
        balance=float(selected_debt["balance"]),
        apr=float(selected_debt["apr"]),
        payment=float(planned_payment),
        start_date=start,
    )
    st.success(
        f"Estimated payoff in **{result.months} months** • Payoff date approx **{result.payoff_date.isoformat()}** • "
        f"Total interest **${result.total_interest:,.2f}**"
    )

    sched_df = pd.DataFrame(result.schedule)
    st.dataframe(sched_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Could not generate payoff schedule: {e}")
    st.caption("Common cause: payment too low to cover interest when APR > 0.")
