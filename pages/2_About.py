# pages/2_About.py

import streamlit as st
from components.ui import inject_css

st.set_page_config(page_title="About • Lovely1 Solutions", page_icon="ℹ️", layout="wide")
inject_css()

st.title("About")
st.write(
    """
Lovely1 Solutions is a growing suite of tools designed to be practical, export-friendly,
and easy to use across desktop and web.

**Focus areas:**
- Finance organization and payoff planning
- Career tools like resume building and job matching
- Relationship assessments and insights
"""
)

st.markdown("### Roadmap (example)")
st.write("- Member portal + login")
st.write("- Admin dashboard (metrics + app access)")
st.write("- Store integrations (Amazon links + on-site products)")
