from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Any, Tuple
from .priority import STATUS_WEIGHT, safe_float

def monthly_rate(apr_percent: float) -> float:
    return (apr_percent / 100.0) / 12.0

@dataclass
class AmortResult:
    months: int
    payoff_date: date
    total_interest: float
    schedule: List[Dict[str, Any]]

def amortize(balance: float, apr: float, payment: float, start_date: date) -> AmortResult:
    r = monthly_rate(apr)
    if balance <= 0:
        return AmortResult(0, start_date, 0.0, [])
    if payment <= 0:
        raise ValueError("Payment must be greater than 0.")
    if r > 0 and payment <= balance * r:
        raise ValueError("Payment is too low to ever pay off this balance (payment <= interest).")

    sched: List[Dict[str, Any]] = []
    b = balance
    total_int = 0.0
    cur = start_date
    m = 0
    while b > 0.005 and m < 1200:
        interest = b * r
        principal = payment - interest
        if principal > b:
            principal = b
            payment_eff = interest + principal
        else:
            payment_eff = payment
        b2 = b - principal
        total_int += interest
        sched.append({
            "month_index": m + 1,
            "date": cur.isoformat(),
            "starting_balance": round(b, 2),
            "payment": round(payment_eff, 2),
            "principal": round(principal, 2),
            "interest": round(interest, 2),
            "ending_balance": round(b2, 2),
        })
        y, mo = cur.year, cur.month
        mo += 1
        if mo > 12:
            mo = 1
            y += 1
        day = min(cur.day, 28)
        cur = date(y, mo, day)
        b = b2
        m += 1

    return AmortResult(m, cur, float(total_int), sched)

def strategy_order(debts: List[Dict[str, Any]], strategy: str, status_override: bool = True) -> List[Dict[str, Any]]:
    def key(d: Dict[str, Any]) -> Tuple:
        status = d.get("status","Current")
        sev = STATUS_WEIGHT.get(status, 0)
        apr = safe_float(d.get("apr", 0.0))
        bal = safe_float(d.get("balance", 0.0))
        name = str(d.get("name","")).lower()
        group = -sev if status_override else 0
        if strategy == "Avalanche":
            return (group, -apr, -bal, name)
        if strategy == "Snowball":
            return (group, bal, -apr, name)
        return (group, int(d.get("custom_order", 999999)), name)
    return sorted(debts, key=key)

def monthly_plan(debts: List[Dict[str, Any]], strategy: str, extra_payment: float,
                 status_override: bool = True) -> List[Dict[str, Any]]:
    included = [d for d in debts if d.get("include_in_strategy", True) and safe_float(d.get("balance",0.0)) > 0]
    ordered = strategy_order(included, strategy, status_override=status_override)

    plan_rows: List[Dict[str, Any]] = []
    for d in ordered:
        minp = safe_float(d.get("min_payment", 0.0))
        planned = safe_float(d.get("planned_payment", minp))
        ov = d.get("override", None) or {}

        # Base payment starts from planned_payment (defaults to minimum)
        pay = max(minp, planned)

        if ov.get("enabled"):
            extra_ov = safe_float(ov.get("extra_monthly", 0.0))
            mode = ov.get("mode")

            # Backward/alias support
            if mode in ("payment", "monthly", "set_payment"):
                mode = "monthly_payment"
                if "monthly_payment" not in ov and "target_payment" in ov:
                    ov["monthly_payment"] = ov.get("target_payment")
            if mode in ("months", "duration", "set_months"):
                mode = "target_payments"
                if "target_payments" not in ov and "target_months" in ov:
                    ov["target_payments"] = ov.get("target_months")

            if mode == "monthly_payment":
                pay = max(minp, safe_float(ov.get("monthly_payment", pay))) + extra_ov

            elif mode == "target_payments":
                try:
                    target_n = int(ov.get("target_payments", 0))
                except Exception:
                    target_n = 0
                if target_n > 0:
                    solved = _solve_payment_for_months(
                        balance=safe_float(d.get("balance", 0.0)),
                        apr=safe_float(d.get("apr", 0.0)),
                        months=target_n,
                    )
                    pay = max(minp, solved) + extra_ov
        plan_rows.append({"id": d.get("id"), "name": d.get("name",""), "payment": round(pay,2), "kind": "required", "notes":"min/override"})

    remaining_extra = max(0.0, float(extra_payment))
    if remaining_extra > 0 and ordered:
        target = ordered[0]
        plan_rows.append({"id": target.get("id"), "name": target.get("name",""), "payment": round(remaining_extra,2), "kind":"extra", "notes": f"{strategy} extra allocation"})
    return plan_rows

def _solve_payment_for_months(balance: float, apr: float, months: int) -> float:
    if months <= 0:
        return 0.0
    r = monthly_rate(apr)
    if r == 0:
        return balance / months
    denom = 1 - (1 + r) ** (-months)
    if denom <= 0:
        return balance
    return (r * balance) / denom
