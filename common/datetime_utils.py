import datetime


def shortnaturaltime(value) -> str:
    """Convert a datetime to a human-readable string."""
    now = datetime.datetime.now(datetime.UTC)
    delta = now - value

    if delta < datetime.timedelta(minutes=1):
        return 'just now'
    if delta < datetime.timedelta(hours=1):
        return f'{int(delta.total_seconds() // 60)}m'
    if delta < datetime.timedelta(days=1):
        return f'{int(delta.total_seconds() // 3600)}h'
    return f'{delta.days}d'
