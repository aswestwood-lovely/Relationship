# data/apps.py

APPS = [
    {
        "id": "debt_calculator",
        "name": "Debt Calculator",
        "category": "Finance",
        "summary": "Plan payoff strategies, track bills, and forecast your budget with exports.",
        "tags": ["Excel Export", "Payoff Plans", "Budgeting"],
        "access": "Public",  # Public | Member | Admin | Coming Soon
        "page": "Apps",      # used for internal navigation (simple approach)
        "status_note": "",
    },
    {
        "id": "iou_manager",
        "name": "IOU / Personal Loan Manager",
        "category": "Finance",
        "summary": "Track loans you owe or are owed with terms, reminders, and PDF exports.",
        "tags": ["Multi-user", "PDF Export", "Notifications"],
        "access": "Member",
        "page": "Apps",
        "status_note": "Member perks apply",
    },
    {
        "id": "finance_tracker",
        "name": "Finance Tracker",
        "category": "Finance",
        "summary": "Track holdings, performance, and transactions (crypto/stocks/bonds basics).",
        "tags": ["Holdings", "P/L", "Charts"],
        "access": "Member",
        "page": "Apps",
        "status_note": "",
    },
    {
        "id": "resume_builder",
        "name": "Resume Builder",
        "category": "Career",
        "summary": "Build ATS-friendly resumes, tailor to jobs, and export to PDF/Word.",
        "tags": ["ATS", "Templates", "Export"],
        "access": "Public",
        "page": "Apps",
        "status_note": "",
    },
    {
        "id": "relationship_quizzes",
        "name": "Relationship Quiz Suite",
        "category": "Relationships",
        "summary": "Take relationship assessments and get structured insights and recommendations.",
        "tags": ["Assessments", "Recommendations", "Profiles"],
        "access": "Public",
        "page": "Apps",
        "status_note": "",
    },
]
