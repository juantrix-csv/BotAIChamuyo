from typing import Dict, List

from config import settings
from db import repo

THRESHOLDS_PERCENT = [75, 50, 25, 10]


def ensure_user_credits(user_id: int, initial: int = settings.CREDITS_DEFAULT):
    """Ensure a credit record exists for the user."""
    return repo.ensure_credits(user_id, initial)


def get_remaining(user_id: int) -> int:
    """Return the remaining credits for the user."""
    credit = repo.get_credits(user_id)
    if credit is None:
        credit = repo.ensure_credits(user_id, settings.CREDITS_DEFAULT)
    return credit.remaining


def consume(user_id: int, amount: int = settings.CREDITS_COST_PER_MSG) -> Dict[str, List[int]]:
    """Consume credits and return remaining and crossed thresholds."""
    credit = repo.get_credits(user_id)
    if credit is None:
        credit = repo.ensure_credits(user_id, settings.CREDITS_DEFAULT)

    prev_remaining = credit.remaining
    new_remaining = max(prev_remaining - amount, 0)

    initial = credit.initial_credits
    alerted = set(filter(None, (credit.milestones_alerted or "").split(",")))
    crossed: List[int] = []

    for percent in THRESHOLDS_PERCENT:
        threshold_value = initial * percent / 100
        if prev_remaining > threshold_value >= new_remaining and str(percent) not in alerted:
            crossed.append(percent)
            alerted.add(str(percent))

    repo.update_credits(user_id, new_remaining, ",".join(sorted(alerted, key=int)))

    return {"remaining": new_remaining, "crossed_thresholds": crossed}
