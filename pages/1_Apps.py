# pages/1_Apps.py

import streamlit as st
from data.apps import APPS
from components.ui import inject_css, app_card, filter_apps

st.set_page_config(page_title="Apps • Lovely1 Solutions", page_icon="🧩", layout="wide")
inject_css()

st.title("Apps")
st.caption("Search, filter, and open your tools. This page reads from data/apps.py.")

# --- Controls ---
cats = ["All"] + sorted({a["category"] for a in APPS})
access_options = sorted({a["access"] for a in APPS})

c1, c2, c3 = st.columns([1, 1.2, 1.6])
with c1:
    category = st.selectbox("Category", cats, index=0)
with c2:
    access_levels = st.multiselect("Access", access_options, default=access_options)
with c3:
    search = st.text_input("Search", placeholder="Type: resume, export, finance, quiz...")

filtered = filter_apps(APPS, category, access_levels, search)

st.divider()

# --- Selected App Details (simple) ---
selected_id = st.session_state.get("selected_app_id")
selected = next((a for a in APPS if a["id"] == selected_id), None)

left, right = st.columns([1.2, 1])

with right:
    st.markdown("### App Details")
    if selected:
        st.markdown(f"**{selected['name']}**")
        st.write(selected["summary"])
        st.write(f"**Category:** {selected['category']}")
        st.write(f"**Access:** {selected['access']}")
        st.write("**Tags:** " + ", ".join(selected.get("tags", [])))

        st.divider()
        st.markdown("#### Actions (stub)")
        st.button("Open Demo (stub)", disabled=True)
        st.button("Open Full App (stub)", disabled=True)

        st.info(
            "Next step: wire these buttons to open the actual Streamlit app pages or external links."
        )
    else:
        st.write("Click **Open** on any app card to see details here.")

with left:
    st.markdown(f"### Results ({len(filtered)})")
    if not filtered:
        st.warning("No apps match your filters.")
    else:
        cols = st.columns(2)
        for i, app in enumerate(filtered):
            with cols[i % 2]:
                app_card(app)
