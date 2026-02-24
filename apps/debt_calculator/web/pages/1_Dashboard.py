import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# --- Path setup so we can import shared core + app_state ---
BASE = Path(__file__).resolve().parents[2]  # .../apps/debt_calculator
sys.path.insert(0, str(BASE / "shared"))
sys.path.insert(0, str(BASE / "web"))  # so we can import app_state.py

from app_state import (
    get_active_profile,
    list_profiles,
    set_active_profile,
    add_profile,
    rename_profile,
    load_section,
)

st.set_page_config(page_title="Dashboard • Debt Calculator", page_icon="📊", layout="wide")

st.title("Dashboard")
st.caption("High-level totals and quick insights for the active profile (persistent storage).")

# -----------------------------
# Profile Controls
# -----------------------------
profiles_list = list_profiles()
active = get_active_profile()

name_to_id = {p.name: p.id for p in profiles_list}
names = [p.name for p in profiles_list]
current_index = names.index(active.name) if active.name in names else 0

p1, p2, p3 = st.columns([2, 1, 1])

with p1:
    selected_name = st.selectbox("Active profile", names, index=current_index)
    selected_id = name_to_id[selected_name]
    if selected_id != active.id:
        set_active_profile(selected_id)
        st.rerun()

with p2:
    new_profile_name = st.text_input("New profile", value="", placeholder="e.g., Household")
    if st.button("Add Profile"):
        add_profile((new_profile_name or "New Profile").strip())
        st.rerun()

with p3:
    rename_to = st.text_input("Rename active", value="", placeholder="New name")
    if st.button("Rename"):
        rename_profile(active.id, (rename_to or active.name).strip())
        st.rerun()

st.divider()

# -----------------------------
# Load persisted bills
# -----------------------------
bills_payload = load_section("bills")  # {"items": [...]}
bills = (bills_payload or {}).get("items", []) or []

# -----------------------------
# Shortcuts
# -----------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("Go to Bills"):
        st.switch_page("pages/2_Bills.py")
with c2:
    if st.button("Go to Payoff Plan"):
        st.switch_page("pages/3_Payoff_Plan.py")
with c3:
    st.button("Import (next)", disabled=True)
with c4:
    st.button("Export (next)", disabled=True)

st.divider()

if not bills:
    st.info("No bills saved for this profile yet. Go to **Bills** to add your first bill.")
    st.stop()

df = pd.DataFrame(bills)

# Defensive: ensure expected columns exist
for col in ["amount", "min_payment", "apr", "due_day", "name", "notes"]:
    if col not in df.columns:
        df[col] = None

df["amount"] = df["amount"].fillna(0.0).astype(float)
df["min_payment"] = df["min_payment"].fillna(0.0).astype(float)
df["apr"] = df["apr"].fillna(0.0).astype(float)
df["due_day"] = df["due_day"].fillna(1).astype(int)

total_balance = float(df["amount"].sum())
total_min_payment = float(df["min_payment"].sum())
avg_apr = float(df["apr"].mean()) if len(df) else 0.0
bill_count = int(len(df))

m1, m2, m3, m4 = st.columns(4)
m1.metric("Bills", f"{bill_count}")
m2.metric("Total Balance", f"${total_balance:,.2f}")
m3.metric("Total Min Payment", f"${total_min_payment:,.2f}")
m4.metric("Average APR", f"{avg_apr:,.2f}%")

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.markdown("### Bills Overview")
    show_cols = ["name", "amount", "due_day", "apr", "min_payment", "notes"]
    show_cols = [c for c in show_cols if c in df.columns]
    st.dataframe(
        df[show_cols].sort_values(by=["due_day", "name"], na_position="last"),
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.markdown("### Quick Insights")

    st.write("**Top balances**")
    top_bal = df[["name", "amount"]].sort_values("amount", ascending=False).head(5)
    for _, row in top_bal.iterrows():
        st.write(f"- {row['name']}: ${row['amount']:,.2f}")

    st.write("")
    st.write("**Top APRs**")
    top_apr = df[["name", "apr"]].sort_values("apr", ascending=False).head(5)
    for _, row in top_apr.iterrows():
        st.write(f"- {row['name']}: {row['apr']:,.2f}%")

st.divider()

st.markdown("### Charts")

cc1, cc2 = st.columns(2)

with cc1:
    st.write("**Balance by Bill**")
    chart_df = df[["name", "amount"]].set_index("name")
    st.bar_chart(chart_df)

with cc2:
    st.write("**APR by Bill**")
    apr_df = df[["name", "apr"]].set_index("name")
    st.bar_chart(apr_df)
