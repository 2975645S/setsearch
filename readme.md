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

### To-do

- [x] Sign-up/login page
- [x] Search artists on homepage
- [x] Create concert from artist page
  - [x] If the artist edits the concert, make it read-only to anyone who is not superuser or the artist. Display "verified" badge.
  - [x] Add songs to setlist, let user reorder them
    - Starts with empty setlist.
  - [x] Concerts should have an "attended?" button for authenticated users (bar the artist).
  - [x] Blank star rating on concert page. If authenticated, can click to set rating. Average rating
  displayed on concert page and artist page.
- [x] Concert pages must have a comment box.
- [x] Page to modify user profile.
- [x] Page to list upcoming concerts.
- [x] Page to list concerts the user has attended.
- [ ] Artists pages
  - [ ] Most played songs.
  - [x] List of concerts.
  - [x] Visible only to admins, link to user account.

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

The following datasets were processed to build the population data:

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
- [django-bootstrap5 v26.2](https://github.com/zostera/django-bootstrap5)
- [django-select2 v8.4.8](https://django-select2.readthedocs.io/en/stable/)
- [django-unfold v0.85.0](https://unfoldadmin.com/)
- [orjson v3.11.7](https://github.com/ijl/orjson)
- [python-dotenv v1.2.2](https://github.com/theskumar/python-dotenv)
- [zstandard v0.25.0](https://python-zstandard.readthedocs.io/en/latest/)

**JavaScript**

- [Bootstrap v5.3.3](https://getbootstrap.com/)
- [jQuery v3.7.1 and v4.0.0](https://jquery.com/)
  - v3 is only used for select2 compatibility.
- [Select2 v4.0.13](https://select2.org/)
- [Fuse v7.1.0](https://fusejs.io/)

**CSS**

- [Bootstrap v5.3.3](https://getbootstrap.com/)
- [Bootstrap Icons v1.13.1](https://icons.getbootstrap.com/)
- [Select2 Bootstrap5 Theme v1.3.0](https://apalfrey.github.io/select2-bootstrap-5-theme/)