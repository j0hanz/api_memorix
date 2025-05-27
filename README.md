# Memorix API 🧠🎮

A memory card game with leaderboards, user profiles, and performance tracking.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16+-orange.svg)](https://www.django-rest-framework.org/)

## 📖 Table of Contents

- [🎯 Overview](#overview)
- [✨ Features](#features)
- [🚀 Quick Start](#quick-start)
- [📱 API Documentation](#api-documentation)
- [🏗️ Architecture](#architecture)
- [🔧 Configuration](#configuration)
- [🛠️ Development](#development)
- [🧪 Testing](#testing)
- [🚢 Deployment](#deployment)
- [🤝 Contributing](#contributing)

---

## 🎯 Overview

Memorix API is a Django REST Framework backend that powers a competitive memory card game. Players match cards across different themed categories, submit their scores, and compete on category-specific leaderboards. The API handles user authentication, score validation, leaderboard management, and profile customization.

### Key Components
- **User Management**: JWT authentication with customizable profiles
- **Game Categories**: Themed card sets (Animals, Nature, Vehicles, etc.)
- **Score System**: Validated game results with anti-cheat measures
- **Leaderboards**: Real-time competitive rankings
- **Background Tasks**: Async leaderboard updates and data processing

---

## ✨ Features

### 🔐 Authentication & Security
- **JWT Token Authentication** with refresh token support
- **Rate Limiting** to prevent abuse (60 score submissions/hour)
- **Input Validation** with cross-field checks to prevent cheating
- **HTTPS & Security Headers** in production
- **CORS Configuration** for frontend integration

### 🎮 Game Mechanics
- **Multiple Categories**: 6 themed card categories
- **Score Validation**: Realistic time/moves/stars combinations
- **Duplicate Prevention**: Unique constraints for identical scores
- **Performance Tracking**: Best scores per category per user

### 🏆 Competitive Features
- **Real-time Leaderboards** updated via background tasks
- **Category-specific Rankings** (top 5 per category)
- **Star Rating System** (1-5 stars based on performance)
- **Profile Pictures** via Cloudinary integration

### 🛡️ Data Integrity
- **Cross-field Validation**: Prevents impossible game combinations
- **Rate Limiting**: 60 score submissions per hour per user
- **Unique Constraints**: Prevents duplicate identical scores
- **Background Processing**: Async leaderboard updates

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL (production) or SQLite (development)
- Cloudinary account (for image uploads)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/api_memorix.git
   cd api_memorix
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py initialize_data  # Load game categories
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

🎉 **Your API is now running at `http://localhost:8000`**

---

## 📱 API Documentation

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### Authentication Endpoints

| Method | Endpoint                       | Description       | Auth Required |
| ------ | ------------------------------ | ----------------- | ------------- |
| `POST` | `/dj-rest-auth/registration/`  | User registration | ❌             |
| `POST` | `/dj-rest-auth/login/`         | User login        | ❌             |
| `POST` | `/dj-rest-auth/logout/`        | User logout       | ✅             |
| `POST` | `/dj-rest-auth/token/refresh/` | Refresh JWT token | ❌             |

### Game API Endpoints

| Method | Endpoint                                  | Description            | Auth Required |
| ------ | ----------------------------------------- | ---------------------- | ------------- |
| `GET`  | `/api/memorix/categories/`                | List game categories   | ❌             |
| `GET`  | `/api/memorix/categories/{id}/`           | Get category details   | ❌             |
| `POST` | `/api/memorix/results/`                   | Submit game score      | ✅             |
| `GET`  | `/api/memorix/results/`                   | List user's scores     | ✅             |
| `GET`  | `/api/memorix/results/best/`              | Get user's best scores | ✅             |
| `GET`  | `/api/memorix/leaderboard/`               | Global leaderboard     | ❌             |
| `GET`  | `/api/memorix/leaderboard/?category={id}` | Category leaderboard   | ❌             |

### User Profile Endpoints

| Method  | Endpoint              | Description            | Auth Required |
| ------- | --------------------- | ---------------------- | ------------- |
| `GET`   | `/api/profiles/`      | List all profiles      | ❌             |
| `GET`   | `/api/profiles/{id}/` | Get profile details    | ❌             |
| `PUT`   | `/api/profiles/{id}/` | Update own profile     | ✅             |
| `PATCH` | `/api/profiles/{id}/` | Partial profile update | ✅             |

### Example Requests

#### Submit a Game Score
```bash
curl -X POST http://localhost:8000/api/memorix/results/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "ANIMALS",
    "moves": 24,
    "time_seconds": 45,
    "stars": 4
  }'
```

#### Get Category Leaderboard
```bash
curl -X GET "http://localhost:8000/api/memorix/leaderboard/?category=1"
```

### Response Formats

#### Success Response (Score Submission)
```json
{
  "id": 1,
  "username": "player123",
  "category_name": "Animals",
  "moves": 24,
  "time_seconds": 45,
  "stars": 4,
  "completed_at": "2m"
}
```

#### Error Response
```json
{
  "moves": ["Moves must be between 1 and 10000"],
  "time_seconds": ["Time too short for the number of moves"]
}
```

---

## 🏗️ Architecture

### Database Schema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User (Django) │    │     Profile     │    │    Category     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │ ◄──┤ owner (FK)      │    │ id (PK)         │
│ username        │    │ id (PK)         │    │ name            │
│ email           │    │ profile_picture │    │ code (UNIQUE)   │
│ password        │    │ created_at      │    │ description     │
└─────────────────┘    │ updated_at      │    └─────────────────┘
                       └─────────────────┘              │
                               │                        │
                               │ 1:Many                 │ 1:Many
                               ▼                        ▼
                       ┌─────────────────────────────────────────┐
                       │                Score                    │
                       ├─────────────────────────────────────────┤
                       │ id (PK)                                 │
                       │ profile_id (FK)                         │
                       │ category_id (FK)                        │
                       │ moves (1-10000)                         │
                       │ time_seconds (1-86400)                  │
                       │ stars (1-5)                             │
                       │ completed_at                            │
                       │ UNIQUE(profile, category, moves,        │
                       │        time_seconds, stars)             │
                       └─────────────────────────────────────────┘
                               │
                               │ 1:1
                               ▼
                       ┌─────────────────┐
                       │   Leaderboard   │
                       ├─────────────────┤
                       │ id (PK)         │
                       │ score_id (FK)   │
                       │ category_id(FK) │
                       │ rank (1-1000)   │
                       │ UNIQUE(category,│
                       │        rank)    │
                       └─────────────────┘
```

### Application Structure

```
api_memorix/
├── 🌐 api/                   # Main configuration
│   ├── settings.py           # Django + DRF settings
│   ├── urls.py               # Root URL routing
│   ├── permissions.py        # Custom DRF permissions
│   └── serializers.py        # JWT & user serializers
├── 🎮 memorix/               # Core game functionality
│   ├── models.py             # Category, Score, Leaderboard
│   ├── serializers.py        # DRF serializers with validation
│   ├── views.py              # ViewSets with custom actions
│   ├── tasks.py              # Background leaderboard updates
│   └── management/commands/  # Data initialization
├── 👥 users/                 # User management
│   ├── models.py             # Profile with Cloudinary images
│   ├── serializers.py        # Profile serialization
│   └── views.py              # Profile ViewSet
└── 🔧 common/                # Shared utilities
    ├── constants.py          # Game constants & validation
    ├── score.py              # Score processing logic
    ├── leaderboard.py        # Ranking algorithms
    └── datetime.py           # Human-readable formatting
```

### Design Patterns

- **ViewSet Patterns**: `ReadOnlyModelViewSet` for public data, `ModelViewSet` for user-owned data
- **Permission Classes**: `IsOwnerOrReadOnly` for user-specific resources
- **Background Tasks**: Async leaderboard updates via django-background-tasks
- **Signal Handlers**: Auto profile creation and leaderboard updates
- **Computed Fields**: `SerializerMethodField()` for dynamic data

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Security
SECRET_KEY=your-secret-key-here
DEBUG=True  # Remove for production

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/memorix_db

# Cloudinary (for image uploads)
CLOUDINARY_NAME=your_cloud_name
CLOUDINARY_KEY=your_api_key
CLOUDINARY_SECRET=your_api_secret

# CORS & CSRF (adjust for your frontend)
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CSRF_TRUSTED_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Game Categories

The system includes 6 pre-defined categories:

| Category | Code       | Description                 |
| -------- | ---------- | --------------------------- |
| Animals  | `ANIMALS`  | Animal-themed memory cards  |
| Nature   | `NATURE`   | Nature-themed memory cards  |
| Vehicles | `VEHICLES` | Vehicle-themed memory cards |
| Food     | `FOOD`     | Food-themed memory cards    |
| Shapes   | `SHAPES`   | Shape-themed memory cards   |
| Numbers  | `NUMBERS`  | Number-themed memory cards  |

### Rate Limiting

| User Type     | Endpoint         | Limit    |
| ------------- | ---------------- | -------- |
| Anonymous     | General API      | 100/hour |
| Authenticated | General API      | 500/hour |
| Authenticated | Score submission | 60/hour  |
| All users     | Authentication   | 5/minute |

---

## 🛠️ Development

### Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Run linting
ruff check .

# Run formatting
ruff format .

# Fix auto-fixable issues
ruff check --fix .
```

### Development Commands

```bash
# Load game categories
python manage.py initialize_data

# Update leaderboards manually
python manage.py initialize_data --leaderboards-only

# Run background tasks
python manage.py process_tasks

# Create test data
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('testuser', 'test@example.com', 'pass123')
```

### API Testing

Use the Django REST Framework browsable API:
- Visit `http://localhost:8000/api/` when `DEBUG=True`
- Interactive forms for testing endpoints
- Authentication via session or JWT tokens

### Database Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test memorix
python manage.py test users

# Run with coverage
pip install coverage
coverage run manage.py test
coverage report
coverage html  # Generates htmlcov/index.html
```

### Test Structure

- **Model Tests**: Validation, constraints, and relationships
- **API Tests**: Endpoint functionality and permissions
- **Security Tests**: Rate limiting and input validation
- **Integration Tests**: End-to-end game flow

### Example Test Command
```bash
# Test score submission with validation
python manage.py test memorix.tests.ScoreAPITest.test_create_score_validation_errors
```

---

## 🚢 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Remove DEBUG from .env
   unset DEBUG

   # Set production database
   DATABASE_URL=postgres://user:pass@prod-host:5432/memorix
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Security Settings**
   - HTTPS enforcement enabled automatically
   - Security headers configured
   - Secure cookie settings

### Heroku Deployment

```bash
# Install Heroku CLI and login
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgres://...
heroku config:set CLOUDINARY_NAME=your-cloud-name

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py initialize_data
```

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow code style guidelines (Ruff)
   - Add tests for new functionality
   - Update documentation as needed
4. **Run tests**
   ```bash
   python manage.py test
   ruff check .
   ```
5. **Submit a pull request**

### Reporting Issues

Please use GitHub Issues for:
- 🐛 Bug reports
- 💡 Feature requests
- 📖 Documentation improvements
- ❓ Questions about usage

---

## 🙏 Acknowledgments

- [Django REST Framework](https://www.django-rest-framework.org/) for the excellent API framework
- [Cloudinary](https://cloudinary.com/) for image hosting services
- [Heroku](https://heroku.com/) for easy deployment platform

