from background_task import background

from common.leaderboard import update_leaderboard_async
from memorix.management.commands.initialize_data import Command


@background(schedule=60, remove_existing_tasks=True)
def initialize_memorix_data_task():
    """Initialize data in the background."""
    cmd = Command()
    cmd.handle()


@background(schedule=5)
def update_leaderboard_task(category_id):
    """Update leaderboard for a category in the background."""
    update_leaderboard_async(category_id)
