import datetime

from common.constants import (
    DAY_HOURS,
    HOUR_MINUTES,
    MINUTE_SECONDS,
    WEEK_DAYS,
)


def shortnaturaltime(value) -> str:
    """Format a datetime object into a human-readable string."""
    now = datetime.datetime.now(datetime.UTC)
    delta = now - value
    seconds = int(delta.total_seconds())
    minutes = seconds // MINUTE_SECONDS
    hours = seconds // (HOUR_MINUTES * MINUTE_SECONDS)
    days = delta.days
    weeks = days // WEEK_DAYS

    if seconds < MINUTE_SECONDS:
        result = f'{seconds}s'
    elif minutes < HOUR_MINUTES:
        result = f'{minutes}m'
    elif hours < DAY_HOURS:
        result = f'{hours}h'
    elif days < WEEK_DAYS:
        result = f'{days}d'
    else:
        result = f'{weeks}w'

    return result


def format_completed_at(completed_at):
    """Format the completed_at datetime"""
    return shortnaturaltime(completed_at) if completed_at else None
