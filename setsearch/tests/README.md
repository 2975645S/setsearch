# SetSearch Tests

Tests for our app **Setsearch** !

## Test Structure (23 tests)

- `test_models_artists.py` (5 tests)
- `test_models_concerts.py` (4 tests)
- `test_api_concerts.py` (6 tests)
- `test_api_comments.py` (7 tests)
- `test_api_artists.py` (1 test)

## Running Tests

### Option 1: Using Django's test runner
```bash
python manage.py test setsearch.tests
uv run python manage.py test setsearch.tests
```

### Option 2: Using the custom test runner
```bash
python run_tests.py
uv run python run_tests.py
```

### Option 3: Run specific test files
```bash
python manage.py test setsearch.tests.test_models_artists
uv run python manage.py test setsearch.tests.test_models_artists

python manage.py test setsearch.tests.test_views_auth
uv run python manage.py test setsearch.tests.test_views_auth
```

## Test Coverage

The tests cover:

### Models
- **Artist**: Creation, slug generation, uniqueness, string representation, user relationships
- **Concert**: Creation, name generation, date handling with different precisions, validation, relationships
- **Venue**: Creation, string representation, optional fields

### Views
- **Authentication**: Login, signup, logout functionality, redirects for authenticated users

## Environment Setup

Make sure you have all dependencies installed:
```bash
uv sync
```

Or with pip:
```bash
pip install -r requirements.txt
```

## Adding New Tests

**When adding new tests please:**

1. Create a new test file in this directory following the naming convention `test_*.py`
2. Use Django's `TestCase` for model and view tests
3. Follow the existing patterns for setup and assertions
4. Run tests to ensure they pass before committing

