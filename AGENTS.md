# AGENTS.md

## Scope
- Applies to the whole repo at `/home/javier/projects-dockploy/fluency`.
- Single Django project with multiple first-party apps: `accounts`, `core`, `daily_tasks`, `fluency`, and `support_library`.

## Sources Of Truth
- There is no root `README`, CI workflow, pre-commit config, task runner config, or repo-local OpenCode config.
- Trust the checked-in Django settings, URLs, migrations, tests, and `Dockerfile` over generic Django assumptions.

## Runtime And Entrypoints
- Use the repo virtualenv locally: `.venv/bin/python`.
- Main entrypoint: `manage.py`.
- Default settings module: `config.settings`.
- Root routing lives in `config/urls.py`.
- `/` is `core:root` and redirects to login or `/dashboard/`; the authenticated landing page is `core:dashboard`.
- App mounts: `/accounts/`, `/daily-tasks/`, `/writing/`, `/support-library/`, `/summernote/`, and `/admin/`.
- The writing-practice module lives in the `fluency` app under `/writing/` with `home`, `level/`, and `daily/` routes.
- Deployment entrypoint is `config.wsgi:application`.

## Verified Commands
- Start dev server: `.venv/bin/python manage.py runserver`
- Local dev helper: `./run_local.sh`
- Run system checks: `.venv/bin/python manage.py check`
- Run all tests: `.venv/bin/python manage.py test`
- Run one test module/class/method: `.venv/bin/python manage.py test fluency.tests.test_views`, `.venv/bin/python manage.py test fluency.tests.test_views.FluencyViewTests`, `.venv/bin/python manage.py test fluency.tests.test_views.FluencyViewTests.test_home_page_renders`
- Create migrations: `.venv/bin/python manage.py makemigrations`
- Verify no missing migrations: `.venv/bin/python manage.py makemigrations --check`
- Apply migrations: `.venv/bin/python manage.py migrate`

## Verification Expectations
- For settings, routes, templates, or view changes, run `.venv/bin/python manage.py check` at minimum.
- If you touch models or migrations, also run `.venv/bin/python manage.py makemigrations --check`.
- `manage.py test` requires a reachable PostgreSQL database with working `DB_*` credentials; there is no SQLite fallback in checked-in settings.

## Environment And Data Quirks
- `config/settings.py` reads env vars directly via `os.getenv`; there is no `.env` loader.
- `run_local.sh` shows the expected local env vars: `APP_ENV=local`, `DEBUG=True`, `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, and `DB_*`.
- `APP_ENV` controls local-vs-nonlocal behavior. If `APP_ENV` is not `local`, `DJANGO_SECRET_KEY` is mandatory and `DEBUG` defaults to `False`.
- `DEBUG` is string-compared: only the exact string `True` enables it.
- `ALLOWED_HOSTS` comes from a comma-separated env var and defaults to `127.0.0.1,localhost`.
- The database backend is always PostgreSQL in checked-in settings.
- `accounts.signals` runs on `post_migrate` to create the default groups `Admin` and `Usuario` and attach admin permissions for `accounts`, `daily_tasks`, and `support_library`.
- Several tests rely on migration-seeded data, including `fluency` catalog slugs, the 12 seeded daily tasks, and seeded support-library titles, seasons, and episodes.

## Deploy / Static Files
- The container installs dependencies from `requirements.txt`; if you add a runtime dependency, update that file.
- Container startup runs `python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}`.
- `whitenoise` serves static files from `STATIC_ROOT = BASE_DIR / 'staticfiles'` using `CompressedManifestStaticFilesStorage`.

## Editing Conventions Observed Here
- Preserve single-quoted Python strings when touching existing files.
- Keep small app-specific behavior inside the existing app unless there is a concrete reason to split it further.
