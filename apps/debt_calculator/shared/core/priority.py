from __future__ import annotations
from datetime import date
from typing import Dict, List, Tuple, Any

STATUS_WEIGHT = {
    "Current": 0,
    "30 Days Past Due": 1,
    ">30 Days Past Due": 2,
}

def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

def safe_date(d: str | None) -> date | None:
    if not d:
        return None
    try:
        y, m, dd = [int(p) for p in d.split("-")]
        return date(y, m, dd)
    except Exception:
        return None

def priority_sort_key(item: Dict[str, Any]) -> Tuple:
    status = item.get("status", "Current")
    sev = STATUS_WEIGHT.get(status, 0)
    apr = safe_float(item.get("apr", 0.0))
    bal = safe_float(item.get("balance", 0.0))
    minp = safe_float(item.get("min_payment", 0.0))
    due = safe_date(item.get("due_date"))
    due_ord = due.toordinal() if due else 99999999
    return (-sev, -apr, -bal, -minp, due_ord, str(item.get("name","")).lower())

def rank_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sorted_items = sorted(items, key=priority_sort_key)
    ranked = []
    for i, it in enumerate(sorted_items, start=1):
        it2 = dict(it)
        it2["priority_rank"] = i
        it2["priority_reason"] = _reason(it2)
        ranked.append(it2)
    return ranked

def _reason(item: Dict[str, Any]) -> str:
    status = item.get("status","Current")
    apr = safe_float(item.get("apr", 0.0))
    bal = safe_float(item.get("balance", 0.0))
    if status in (">30 Days Past Due","30 Days Past Due"):
        return f"{status} + {apr:.2f}% APR"
    if apr >= 20:
        return f"High APR {apr:.2f}%"
    if bal >= 5000:
        return f"High Balance ${bal:,.0f}"
    return "Due date / minimum driven"
