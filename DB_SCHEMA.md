# Memorix Entity Relationship Diagram

## Database Schema

```
+---------------------+        +-----------------------+        +----------------------+
|    User (Django)    |        |       Profile         |        |      Category        |
+=====================+        +======================+        +======================+
| id          INT PK  |<-------| owner       INT FK(1) |        | id          INT PK   |
| username    VARCHAR |        | id          INT PK    |        | name        VARCHAR  |
| password    VARCHAR |        | profile_pic URL       |        | code        VARCHAR  |
| email       VARCHAR |        | created_at  DATETIME  |        | description TEXT     |
| is_staff    BOOLEAN |        | updated_at  DATETIME  |        | created_at  DATETIME |
| date_joined DATETIME|        |                       |        |                      |
+---------------------+        +-----------------------+        +----------------------+
                                     |                               |
                                     | 1:Many                        | 1:Many
                                     ↓                               ↓
                              +---------------------------------+
                              |             Score               |
                              +=================================+
                              | id             INT PK           |
                              | profile_id     INT FK           |
                              | category_id    INT FK           |
                              | moves          INT              |
                              | time_seconds   INT              |
                              | stars          INT              |
                              | completed_at   DATETIME         |
                              +---------------------------------+
                                     |                |
                                     | 1:1           | 1:Many
                                     ↓                ↓
                                     |         +-------------------------+
                                     |         |      Leaderboard        |
                                     |         +=========================+
                                     +-------->| id          INT PK      |
                                               | score_id    INT FK(1)   |
                                               | category_id INT FK      |
                                               | rank        INT         |
                                               +-------------------------+
```

## Constraints & Validation

### Unique Constraints
- **Score**: `(profile_id, category_id, moves, time_seconds, stars)`
- **Leaderboard**: `(category_id, rank)`

### Field Validation

#### Category Model
- **name**: Max length: 100 characters (defined by [`CATEGORY_NAME_MAX_LENGTH`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py))
- **code**: Max length: 50 characters (defined by [`CATEGORY_CODE_MAX_LENGTH`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py)), Must be unique
- **description**: Max length: 500 characters (defined by [`CATEGORY_DESCRIPTION_MAX_LENGTH`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py))

#### Score Model
- **moves**: Min: 1 (defined by [`MIN_MOVES`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py)), Max: 10000 (defined by [`MAX_MOVES`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py))
- **time_seconds**: Min: 1 (defined by [`MIN_TIME_SECONDS`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py)), Max: 86400 (24 hours, defined by [`MAX_TIME_SECONDS`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py))
- **stars**: Min: 1 (defined by [`MIN_STARS`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py)), Max: 5 (defined by [`MAX_STARS`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py))

#### Leaderboard Model
- **rank**: Min: 1, Max: 1000 (defined by [`MAX_LEADERBOARD_RANK`](e%3A%5Capi_drf%5Ccommon%5Cconstants.py)), Must be unique per category

## Relationships

| Relationship           | Type        | Description                                 |
| ---------------------- | ----------- | ------------------------------------------- |
| User → Profile         | One-to-One  | Each user has exactly one profile           |
| Profile → Score        | One-to-Many | A profile can have multiple scores          |
| Category → Score       | One-to-Many | A category can have multiple scores         |
| Score → Leaderboard    | One-to-One  | Each score may appear once in a leaderboard |
| Category → Leaderboard | One-to-Many | A category has multiple leaderboard entries |
