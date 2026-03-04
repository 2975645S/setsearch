# SetSearch

Built by [2975645S](https://github.com/2975645S), [2961649C](https://github.com/crawfordclarke), [2839497C](https://github.com/2839497C), and [2972355H](#) for [Web Application Development 2](https://www.gla.ac.uk/coursecatalogue/course/?code=COMPSCI2021).

## Development

Make sure you install the pre-commit hooks by running:

```bash
uv run pre-commit install
```

## Running the code

### Preparation

One thing you need to do to prepare is populate your `.env` file. To make this easier, a template file is
provided in [`.env.example`](.env.example). If you don't want to do this yourself, you can run the provided [
`env.py`](scripts/env.py)
script and it will automatically be populated for you. You must also migrate the database. You can do these two things
with the following commands:

```bash
python scripts/env.py
python manage.py migrate
```

### Execution

If you have [uv](https://github.com/astral-sh/uv) installed, migrate the database and run the server:

```bash
uv run manage.py runserver
```

Otherwise, you must make sure you have installed **Python 3.13.12** and need to set up your virtual environment with:

```bash
python -m venv .venv
pip install .
```

You can then migrate the database and run the server:

```bash
python manage.py runserver
```

## Acknowledgements

SetSearch is built on top of the following projects:

- [Django v6.0.3](https://www.djangoproject.com/)
- [Django Bootstrap 5 v26.2](https://django-bootstrap5.readthedocs.io/en)
- [Django Google Fonts v0.0.3](https://github.com/andymckay/django-google-fonts)
- [python-dotenv v1.2.2](https://github.com/theskumar/python-dotenv)
