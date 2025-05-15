from background_task import background

from memorix.management.commands.initialize_data import Command


@background(schedule=60, remove_existing_tasks=True)
def initialize_memorix_data_task():
    """Initialize data in the background."""
    cmd = Command()
    cmd.handle()
