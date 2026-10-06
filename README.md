# Backlog Vault

> Steam for people with an empty wallet and a full backlog.

Backlog Vault is a Django app where gamers track their game library: what
they plan to play, what they are playing, what they finished and what they
dropped, with ratings, hours and notes. Gamers also build shared collections
of games, and a small moderation team keeps the catalog tidy.

## Features

- **Catalog** of games with genres, platforms and developers: search,
  genre/platform filters, pagination, cover images (upload or URL).
- **Personal library** (a through-model with status, rating 1-10, hours,
  dates and notes, protected by database constraints).
- **Collections**: curated lists of games, with add/remove straight from a
  game page.
- **Profiles** with statistics: games by status, hours, average rating,
  most played genre, progress bar.
- **Roles**: regular users, moderators and admins (see below).
- **Registration with account activation** (link printed to the console).
- **Dark/light theme** switch and a custom admin panel
  ([django-unfold](https://unfoldadmin.com/)).

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data      # demo data + demo users
python manage.py runserver
```

Open http://127.0.0.1:8000/. In development the header has a **Demo** menu
that signs you in as the admin, a moderator or a regular user in one click.

## Demo accounts

All demo accounts use the password `testpass123`.

| Username                 | Role           | What they can do                            |
|--------------------------|----------------|---------------------------------------------|
| `demo_admin`             | Admin          | Everything, including the admin panel       |
| `demo_moderator`         | Moderator      | Manage games, genres, platforms, developers |
| `demo_user`              | Regular player | Library, ratings, collections, own profile  |
| `alex`, `maria`, `taras` | Players        | Extra sample users with libraries           |

## Roles and permissions

| Action                                          | Guest | Player |    Moderator     |  Admin  |
|-------------------------------------------------|:-----:|:------:|:----------------:|:-------:|
| Browse catalog and game pages                   |   +   |   +    |        +         |    +    |
| Browse collections, profiles                    |   -   |   +    |        +         |    +    |
| Manage own library, collections, profile        |   -   |   +    |        +         |    +    |
| Create / edit / delete games and reference data |   -   |   -    |        +         |    +    |
| Open the admin panel                            |   -   |   -    | + (catalog only) | + (all) |
| Activate accounts, make moderators              |   -   |   -    |        -         |    +    |
| Comment on games and collections                |   -   |   +    |        +         |    +    |
| Delete own comments                             |   -   |   +    |        +         |    +    |
| Delete any comment                              |   -   |   -    |        +         |    +    |

Moderators are regular gamers who are *staff* and belong to the `Moderators`
group (created by `python manage.py setup_roles`, also run by `seed_data`).
In the admin, select gamers and use **Make selected gamers moderators**.

## Registration and activation

New accounts are created **inactive**. The app generates an activation link
and prints the e-mail to the server console (no real e-mail is sent). Open
that link to activate the account and sign in, or ask a moderator or admin to
run **Activate selected gamers** in the admin panel. Switching to real e-mail
only needs the usual `EMAIL_*` / `MAILERS` settings.

## Configuration

| Environment variable   | Default          | Purpose                                   |
|------------------------|------------------|-------------------------------------------|
| `DJANGO_SECRET_KEY`    | insecure dev key | Secret key (set it in production)         |
| `DJANGO_DEBUG`         | `1`              | `0` turns debug off                       |
| `DJANGO_ALLOWED_HOSTS` | empty            | Comma separated host names                |
| `DJANGO_DEMO_MODE`     | same as debug    | Demo login menu (never use in production) |

Uploaded covers are stored in `media/` (ignored by git).

## Database

![Database diagram](docs/backlog_vault_db.png)

The editable source is `docs/backlog_vault_db.drawio`.

## Project structure

```
backlog_vault/        project settings and urls
vault/
  models.py           Gamer, Genre, Platform, Developer, Game,
                      LibraryEntry, Collection
  views/              views split by section (games, library, ...)
  forms.py, mixins.py, roles.py, emails.py, backends.py, signals.py
  management/commands seed_data, setup_roles
  tests/              test suite
templates/            base, includes and one folder per section
```

## Tests and code style

```bash
python manage.py test
flake8
```

GitHub Actions runs both on every pull request.
