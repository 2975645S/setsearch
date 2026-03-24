# SetSearch

Built
by [2975645S](https://github.com/2975645S), [2961649C](https://github.com/crawfordclarke), [2839497C](https://github.com/2839497C),
and [2972355H](#) for [Web Application Development 2](https://www.gla.ac.uk/coursecatalogue/course/?code=COMPSCI2021).

## Development

Prepare for development:

```bash
uv sync --all-groups
python script/env.py
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

3. Populate the database:
  - This will automatically migrate your database for you!

```bash
python population_script.py
```

### Execution

```bash
python manage.py runserver
```

## Acknowledgements

### Data

- The following datasets were provided by [MusicBrainz](https://musicbrainz.org/) under the
  [CC0 1.0 Universal License](https://creativecommons.org/publicdomain/zero/1.0/).
    - [artist](https://data.metabrainz.org/pub/musicbrainz/data/json-dumps/20260304-001001/artist.tar.xz) dataset (~15.3GB)
    - [event](https://data.metabrainz.org/pub/musicbrainz/data/json-dumps/20260311-001001/event.tar.xz) (~476MB)
    - [release](https://data.metabrainz.org/pub/musicbrainz/data/json-dumps/20260304-001001/release.tar.xz) dataset
      (~301GB)
- Artist popularity data is
  from [Music Artists Popularity on Kaggle](https://www.kaggle.com/datasets/pieca111/music-artists-popularity), licensed
  under the [CC BY-SA 4.0 License](https://creativecommons.org/licenses/by-sa/4.0/).

### Dependencies

SetSearch uses:

**Python**

- [django v6.0.3](https://www.djangoproject.com/)
- [django-bootstrap5 v26.2](https://django-bootstrap5.readthedocs.io/en/latest/)
- [django-select2 v8.4.8](https://django-select2.readthedocs.io/en/8.4.8/)
- [django-unfold v0.86.1](https://github.com/unfoldadmin/django-unfold)
- [orjson v3.11.7](https://github.com/ijl/orjson)
- [python-dotenv v1.2.2](https://saurabh-kumar.com/python-dotenv/)
- [zstandard v0.25.0](https://python-zstandard.readthedocs.io/en/0.25.0/)

**JavaScript**

- [Bootstrap v5.3.3](https://getbootstrap.com/docs/5.3)
- [jQuery v3.7.1 and v4.0.0](https://jquery.com/)
  - v3 is only used for select2 compatibility.
- [Select2 v4.0.13](https://select2.org/)
- [SortableJS v1.15.7](https://sortablejs.github.io/Sortable/)
- [jquery-sortablejs v1.0.1](https://github.com/SortableJS/jquery-sortablejs/tree/1.0.0)
- [Fuse v7.1.0](https://fusejs.io/)

**CSS**

- [Bootstrap v5.3.3](https://getbootstrap.com/docs/5.3)
- [Bootstrap Icons v1.13.1](https://icons.getbootstrap.com/)
- [Select2 Bootstrap5 Theme v1.3.0](https://apalfrey.github.io/select2-bootstrap-5-theme/)