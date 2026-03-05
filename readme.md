# SetSearch

Built
by [2975645S](https://github.com/2975645S), [2961649C](https://github.com/crawfordclarke), [2839497C](https://github.com/2839497C),
and [2972355H](#) for [Web Application Development 2](https://www.gla.ac.uk/coursecatalogue/course/?code=COMPSCI2021).

## Development

Install pre-commit hooks:

```bash
uv run pre-commit install
```

## Running the code

### Preparation

1. Setup **Python 3.13.12** virtual environment and install dependencies:

```bash
python -m venv .venv
pip install -r requirements.txt
```

2. Populate your `.env` file using the template `[.env.example](.env.example)` or run the script:

```bash
python scripts/env.py
```

3. Apply database migrations:

```bash
python manage.py migrate
```

4. Populate the database:

```bash
python populate.py
```

### Execution

```bash
python manage.py runserver
```

## Acknowledgements

### Data

- Song data is provided by [MusicBrainz](https://musicbrainz.org/) under the
  [CC0 1.0 Universal License](https://creativecommons.org/publicdomain/zero/1.0/).
    - [release](https://data.metabrainz.org/pub/musicbrainz/data/json-dumps/20260304-001001/release.tar.xz) dataset
      (301GB)
- Artist popularity data is
  from [Music Artists Popularity on Kaggle](https://www.kaggle.com/datasets/pieca111/music-artists-popularity), licensed
  under the [CC BY-SA 4.0 License](https://creativecommons.org/licenses/by-sa/4.0/).

### Dependencies

SetSearch uses:

- [Django v6.0.3](https://www.djangoproject.com/)
- [Django Bootstrap 5 v26.2](https://django-bootstrap5.readthedocs.io/en)
- [Django Google Fonts v0.0.3](https://github.com/andymckay/django-google-fonts)
- [kagglehub v1.0.0](https://github.com/Kaggle/kagglehub)
- [orjson v3.11.7](https://github.com/ijl/orjson)
- [pandas v3.0.1](https://pandas.pydata.org/)
- [python-dotenv v1.2.2](https://github.com/theskumar/python-dotenv)
- [requests v2.32.5](https://docs.python-requests.org/en/latest/)
- [zstandard v0.25.0](https://python-zstandard.readthedocs.io/en/latest/)