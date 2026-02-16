# components/ui.py

import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>
          .block-container { padding-top: 2.0rem; padding-bottom: 3rem; }
          .app-card {
              border: 1px solid rgba(49,51,63,.2);
              border-radius: 16px;
              padding: 16px 16px 14px 16px;
              background: rgba(255,255,255,0.03);
              margin-bottom: 14px;
          }
          .muted { opacity: 0.75; }
          .tag {
              display: inline-block;
              padding: 2px 10px;
              border-radius: 999px;
              border: 1px solid rgba(49,51,63,.2);
              margin-right: 6px;
              margin-top: 6px;
              font-size: 0.8rem;
              opacity: 0.9;
          }
          .badge {
              display: inline-block;
              padding: 3px 10px;
              border-radius: 999px;
              font-size: 0.8rem;
              border: 1px solid rgba(49,51,63,.2);
              margin-left: 8px;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

def access_badge(access: str) -> str:
    # simple visual cue using text (Streamlit doesn't allow custom colors reliably without more CSS)
    if access == "Public":
        return "✅ Public"
    if access == "Member":
        return "⭐ Member"
    if access == "Admin":
        return "🛡️ Admin"
    if access == "Coming Soon":
        return "🚧 Coming Soon"
    return access

def app_card(app: dict):
    st.markdown('<div class="app-card">', unsafe_allow_html=True)

    title = f"**{app['name']}** <span class='badge'>{access_badge(app['access'])}</span>"
    st.markdown(title, unsafe_allow_html=True)
    st.markdown(f"<div class='muted'>{app['summary']}</div>", unsafe_allow_html=True)

    tags_html = "".join([f"<span class='tag'>{t}</span>" for t in app.get("tags", [])])
    st.markdown(tags_html, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        if st.button("Details", key=f"details_{app['id']}"):
            st.session_state["selected_app_id"] = app["id"]
            st.switch_page("pages/1_Apps.py")

    with c2:
        # If there's a demo URL, use it; otherwise go to details page
        if app.get("demo_url"):
            st.link_button("Open Demo", app["demo_url"])
        else:
            if st.button("Open Demo", key=f"demo_{app['id']}"):
                st.session_state["selected_app_id"] = app["id"]
                st.switch_page("pages/1_Apps.py")

    with c3:
        if app.get("docs_url"):
            st.link_button("Docs", app["docs_url"])
        else:
            st.button("Docs", disabled=True, key=f"docs_{app['id']}")

    st.markdown("</div>", unsafe_allow_html=True)

def filter_apps(apps, category, access_levels, search_text):
    out = []
    s = (search_text or "").strip().lower()

    for a in apps:
        if category != "All" and a["category"] != category:
            continue
        if access_levels and a["access"] not in access_levels:
            continue
        if s:
            blob = " ".join([
                a["name"], a["summary"], a["category"], " ".join(a.get("tags", []))
            ]).lower()
            if s not in blob:
                continue
        out.append(a)
    return out
