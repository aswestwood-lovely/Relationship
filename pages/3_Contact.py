# pages/3_Contact.py

import streamlit as st
from components.ui import inject_css

st.set_page_config(page_title="Contact • Lovely1 Solutions", page_icon="📬", layout="wide")
inject_css()

st.title("Contact")
st.write("Add your preferred contact method here.")

with st.form("contact_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    message = st.text_area("Message", height=150)
    submitted = st.form_submit_button("Send (stub)")
    if submitted:
        st.success("Received! (This is a stub — next step is wiring to email or a database.)")
