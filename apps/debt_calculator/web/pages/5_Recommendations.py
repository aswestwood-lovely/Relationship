import streamlit as st
import sys
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "shared"))
sys.path.insert(0, str(BASE / "web"))

from app_state import get_active_profile, load_section
import core.payoff as payoff

st.set_page_config(page_title="Recommendations • Debt Calculator", page_icon="✅", layout="wide")

st.title("Recommendations")
st.caption("Actionable suggestions based on your current debts and payoff plan settings.")

active = get_active_profile()
bills = (load_section("bills") or {}).get("items", []) or []

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

if not bills:
    st.info("No bills found. Add bills first.")
    st.stop()

debts = bills_to_debts(bills)

# Controls
c1, c2, c3 = st.columns([1.2, 1, 1])
with c1:
    strategy = st.selectbox("Strategy", ["Avalanche", "Snowball", "Custom"], index=0)
with c2:
    extra_payment = st.number_input("Extra monthly payment", min_value=0.0, step=25.0, value=0.0, format="%.2f")
with c3:
    status_override = st.checkbox("Status override priority", value=True)

plan = payoff.monthly_plan(debts, strategy=strategy, extra_payment=float(extra_payment), status_override=bool(status_override))
plan_df = pd.DataFrame(plan)

st.divider()
st.subheader("What to do next")

recs = []

# 1) Payment too low warning (interest-only risk)
for d in debts:
    if d["apr"] > 0 and d["planned_payment"] > 0:
        monthly_interest = d["balance"] * (d["apr"] / 100.0) / 12.0
        if d["planned_payment"] <= monthly_interest:
            recs.append(
                ("High priority",
                 f"Increase payment for **{d['name']}**. Current planned payment may not cover monthly interest.",
                 f"Monthly interest est: ${monthly_interest:,.2f} vs payment ${d['planned_payment']:,.2f}.")
            )

# 2) Missing min payments
for d in debts:
    if d["balance"] > 0 and d["min_payment"] <= 0:
        recs.append(
            ("High priority",
             f"Add a minimum payment for **{d['name']}**.",
             "Payoff planning works best with a realistic minimum payment.")
        )

# 3) Delinquent/Collections suggestion
for d in debts:
    if str(d.get("status", "")).lower() in {"delinquent", "collections"}:
        recs.append(
            ("Important",
             f"Address **{d['name']}** status = {d.get('status')}.",
             "Consider contacting the creditor and prioritizing stabilization before aggressive extra payments.")
        )

# 4) Plan-based suggestion: focus debt with most extra allocation
if not plan_df.empty:
    extra_alloc = plan_df[plan_df["kind"] == "extra"].copy()
    if not extra_alloc.empty:
        top = extra_alloc.sort_values("payment", ascending=False).head(1).iloc[0]
        recs.append(
            ("Good move",
             f"Your strategy targets **{top['name']}** with the most extra payment.",
             "Stay consistent month to month for best payoff results.")
        )

# 5) General strategy suggestion
recs.append(
    ("Tip",
     f"Use **Avalanche** to minimize interest or **Snowball** for motivation wins.",
     "If you choose Custom, set a clear custom order and review it monthly.")
)

if not recs:
    st.success("No critical issues detected. Your setup looks solid.")
else:
    for level, title, detail in recs:
        st.markdown(f"### {level}: {title}")
        st.write(detail)

st.divider()
st.subheader("Plan preview")
st.dataframe(plan_df, use_container_width=True, hide_index=True)
