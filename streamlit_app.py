# streamlit_app.py

import streamlit as st
from data.apps import APPS
from components.ui import inject_css, app_card

st.set_page_config(
    page_title="Lovely1 Solutions • App Suite",
    page_icon="✨",
    layout="wide",
)

inject_css()

# --- Top header / hero ---
st.title("Lovely1 Solutions")
st.subheader("A practical suite of apps for **finance**, **career**, and **relationships**.")

colA, colB, colC = st.columns([1.4, 1, 1])
with colA:
    st.write(
        "Use these tools to organize your life, make better decisions, and keep everything exportable and reusable."
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Explore Apps"):
            st.switch_page("pages/1_Apps.py")
    with c2:
        st.button("Sign In (coming soon)", disabled=True)

with colB:
    st.markdown("### What you get")
    st.write("✅ Clean UI")
    st.write("✅ Exports (Excel/PDF) where applicable")
    st.write("✅ Built to scale to desktop + web")

with colC:
    st.markdown("### Member perks")
    st.write("⭐ Discounts on products")
    st.write("⭐ Saved profiles / preferences")
    st.write("⭐ Extra features")

st.divider()

# --- Featured apps (pick 2-3) ---
st.markdown("## Featured Apps")
featured_ids = {"debt_calculator", "resume_builder", "relationship_quizzes"}
featured = [a for a in APPS if a["id"] in featured_ids]

f1, f2, f3 = st.columns(3)
for col, app in zip([f1, f2, f3], featured):
    with col:
        app_card(app)

st.divider()

# --- Full catalog preview ---
st.markdown("## App Catalog")
st.caption("Grouped by category. Add apps once in data/apps.py.")

by_cat = {}
for a in APPS:
    by_cat.setdefault(a["category"], []).append(a)

for cat in sorted(by_cat.keys()):
    st.markdown(f"### {cat}")
    items = sorted(by_cat[cat], key=lambda x: x["name"])
    cols = st.columns(3)
    for i, app in enumerate(items):
        with cols[i % 3]:
            app_card(app)

st.divider()

# --- Footer ---
st.caption("© Lovely1 Solutions • Built with Streamlit")
