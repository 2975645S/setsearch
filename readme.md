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
- [ ] Create concert from artist page
  - [ ] If the artist edits the concert, make it read-only to anyone who is not superuser or the artist. Display "verified" badge.
  - [ ] Add songs to setlist, let user reorder them
    - Starts with empty setlist.
  - [ ] Concerts should have an "attended?" button for authenticated users (bar the artist).
  - [ ] Blank star rating on concert page. If authenticated, can click to set rating. Average rating
  displayed on concert page and artist page.
- [X] Concert pages must have a comment box.
- [ ] Page to modify user profile.
- [ ] Page to list upcoming concerts.
- [ ] Page to list concerts the user has attended.
- [ ] Artists pages
  - [ ] Most played songs.
  - [ ] List of concerts.
  - [ ] Visible only to admins, link to user account.

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

- [django v6.0.3](https://www.djangoproject.com/)
- [orjson v3.11.7](https://github.com/ijl/orjson)
- [python-dotenv v1.2.2](https://github.com/theskumar/python-dotenv)
- [zstandard v0.25.0](https://python-zstandard.readthedocs.io/en/latest/)