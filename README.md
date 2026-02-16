# Lovely1 Solutions • Suite

This repository contains the Lovely1 Solutions application suite:
- A Streamlit portfolio (launcher) site
- Multiple apps, each with Desktop + Web variants
- A shared library for common functionality (auth, exports, database, UI helpers)

## Repository Layout


## Apps Included

- Debt Calculator
- IOU / Personal Loan Manager
- Finance Tracker
- Resume Builder
- Relationship Quiz Suite
- Web Scraper
- Data Analytics Tool

## Getting Started (Portfolio)

1. Create and activate a virtual environment
2. Install portfolio requirements
3. Run Streamlit

Example (PowerShell):

```powershell
cd portfolio_web
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
