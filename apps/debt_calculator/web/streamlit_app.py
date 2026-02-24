import streamlit as st
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]  # .../apps/debt_calculator
sys.path.insert(0, str(BASE / "shared"))   # exposes shared/core as package "core"

import core.payoff as payoff
import core.priority as priority
import core.profiles as profiles
import core.storage as storage
import core.data_access as data_access
import core.calendar_utils as calendar_utils
import core.app_paths as app_paths

st.set_page_config(page_title="Debt Calculator (Web)", page_icon="💳", layout="wide")

st.write("✅ Web app loaded")
st.success("✅ Imported core modules successfully!")
