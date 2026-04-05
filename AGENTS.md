# AGENTS.md

## Scope
- Applies to the whole repo at `/home/javier/projects-dockploy/fluency`.
- This is a minimal Django 5.2 project, not a multi-package repo.

## Sources Of Truth
- There is no root `README`, CI workflow, pre-commit config, or task runner config in this repo.
- There is no `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`, or `opencode.json`.
- Trust the checked-in Django files and Dockerfile over generic Django assumptions.

## Runtime And Entrypoints
- Use the repo virtualenv locally: `.venv/bin/python`.
- Main command entrypoint: `manage.py`.
- Django settings module defaults to `config.settings`.
- Root URL config is `config/urls.py`.
- WSGI entrypoint for deployment is `config.wsgi:application`.
- `/` is served by `config.views.home` and returns a simple inline `HttpResponse`.

## Verified Commands
- Start dev server: `.venv/bin/python manage.py runserver`
- Run system checks: `.venv/bin/python manage.py check`
- Run all tests: `.venv/bin/python manage.py test`
- Create migrations: `.venv/bin/python manage.py makemigrations`
- Verify no missing migrations: `.venv/bin/python manage.py makemigrations --check`
- Apply migrations: `.venv/bin/python manage.py migrate`
- Open Django shell: `.venv/bin/python manage.py shell`

## Focused Test Commands
- Single module: `.venv/bin/python manage.py test path.to.tests`
- Single class: `.venv/bin/python manage.py test path.to.tests.MyTestCase`
- Single method: `.venv/bin/python manage.py test path.to.tests.MyTestCase.test_method`
- As of now, `manage.py test` succeeds but discovers `0` tests.

## Verification Expectations
- For settings, URLs, views, or other config-only changes, run `.venv/bin/python manage.py check` at minimum.
- If you add behavior with tests, run the narrowest relevant `manage.py test ...` target first.
- If you add or edit migrations, also run `.venv/bin/python manage.py makemigrations --check`.

## Environment Quirks
- `config/settings.py` reads environment variables directly via `os.getenv`; there is no `.env` loader configured.
- `SECRET_KEY` comes from `DJANGO_SECRET_KEY` with a development fallback.
- `DEBUG` is parsed as `os.getenv('DEBUG', 'True') == 'True'`; only the exact string `True` enables debug.
- `ALLOWED_HOSTS` is parsed from a comma-separated `ALLOWED_HOSTS` env var and defaults to `127.0.0.1,localhost`.
- Django is configured for PostgreSQL via `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.
- Default local database settings are `fluency_local` on `127.0.0.1:5432` with user `fluency_local_user`.
- `APP_ENV` is only used by `config.views.home` for display; it does not switch settings modules or behavior elsewhere.

## Docker / Deploy
- The repo includes a root `Dockerfile` and `.dockerignore`.
- Container build installs from `requirements.txt`; if you add a runtime dependency, update `requirements.txt` or the image will fail.
- Container startup command is `python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}`.
- `PORT` defaults to `8000` in the Dockerfile.

## Tooling Reality
- `requirements.txt` currently pins Django, gunicorn, asgiref, packaging, and sqlparse.
- No linter, formatter, type checker, or pytest config is present.
- Do not claim `ruff`, `black`, `flake8`, `mypy`, or `pytest` are required unless you add and verify that tooling.

## Editing Conventions Observed In Repo
- Keep changes small and local; this codebase is still close to Django defaults.
- Preserve single-quoted Python strings when touching existing files.
- Imports currently follow standard-library then third-party/local grouping with a blank line between groups.
- Keep configuration in `config/settings.py` unless there is a concrete reason to split it.
- Register simple routes directly in `config/urls.py` until a real app module exists.
- There are no first-party Django apps yet beyond the generated `config` package; if you create one, remember to add it to `INSTALLED_APPS`.

## What Not To Assume
- Do not assume production hardening exists just because Docker is present.
- Do not assume `APP_ENV=production` changes settings behavior; it currently does not.
- Do not assume `0.0.0.0` is the browser URL during local debugging; it is only the bind address.
