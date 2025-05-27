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
- **Moves**: Min: 1, Max: 10000
- **Time**: Min: 1s, Max: 86400s (24h)
- **Stars**: Min: 1, Max: 5

## Relationships

| Relationship           | Type        | Description                                 |
| ---------------------- | ----------- | ------------------------------------------- |
| User → Profile         | One-to-One  | Each user has exactly one profile           |
| Profile → Score        | One-to-Many | A profile can have multiple scores          |
| Category → Score       | One-to-Many | A category can have multiple scores         |
| Score → Leaderboard    | One-to-One  | Each score may appear once in a leaderboard |
| Category → Leaderboard | One-to-Many | A category has multiple leaderboard entries |
