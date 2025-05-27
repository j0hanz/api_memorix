# Profile constants
DEFAULT_PROFILE_PICTURE = 'profile_gtdj73'

# Model field lengths
CATEGORY_NAME_MAX_LENGTH = 100
CATEGORY_CODE_MAX_LENGTH = 50
CATEGORY_DESCRIPTION_MAX_LENGTH = 500

# Game constants
MIN_MOVES = 1
MAX_MOVES = 10000
MIN_TIME_SECONDS = 1
MAX_TIME_SECONDS = 86400
MIN_STARS = 1
MAX_STARS = 5
MAX_LEADERBOARD_RANK = 1000

# Cross-validation constants
HIGH_STAR_THRESHOLD = 4  # Stars considered "high" for validation
MAX_MOVES_FOR_HIGH_STARS = 100  # Max moves allowed for high star rating

# Rate limiting constants
DEFAULT_THROTTLE_RATES = {
    'anon': '100/hour',
    'user': '1000/hour',
    'score_submit': '60/hour',
    'auth': '5/min',
}

# Game categories
GAME_CATEGORIES = [
    {
        'name': 'Animals',
        'code': 'ANIMALS',
        'description': 'Animal-themed memory cards',
    },
    {
        'name': 'Nature',
        'code': 'NATURE',
        'description': 'Nature-themed memory cards',
    },
    {
        'name': 'Vehicles',
        'code': 'VEHICLES',
        'description': 'Vehicles-themed memory cards',
    },
    {
        'name': 'Food',
        'code': 'FOOD',
        'description': 'Food-themed memory cards',
    },
    {
        'name': 'Shapes',
        'code': 'SHAPES',
        'description': 'Shapes-themed memory cards',
    },
    {
        'name': 'Numbers',
        'code': 'NUMBERS',
        'description': 'Numbers-themed memory cards',
    },
]

# Datetime constants
JUST_NOW_SECONDS = 10
MINUTE_SECONDS = 60
HOUR_MINUTES = 60
DAY_HOURS = 24
WEEK_DAYS = 7
YESTERDAY_DAYS = 1
