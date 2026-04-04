# AGENTS.md

## Scope
- This file applies to the entire repository at `/home/javier/projects-dockploy/fluency`.
- The repository is currently a minimal Django project.
- Python version in the local virtualenv is `3.12.3`.
- Django version in the local virtualenv is `5.2.12`.

## Current Repository Layout
- `manage.py` is the main entry point for local commands.
- `config/settings.py` contains Django settings.
- `config/urls.py` contains the root URL configuration.
- `config/asgi.py` and `config/wsgi.py` expose deployment entry points.
- There are currently no first-party apps beyond the generated `config` package.
- There are currently no repository test modules.
- There is currently no existing `AGENTS.md`; this file is the canonical agent guide.

## Editor Rule Files
- No `.cursor/rules/` directory was found.
- No `.cursorrules` file was found.
- No `.github/copilot-instructions.md` file was found.
- Agents should not claim additional editor-specific rules exist unless those files are later added.

## Environment Expectations
- Prefer the checked-in virtualenv for local execution: `.venv/bin/python`.
- Run commands from the repository root.
- Assume Django settings module `config.settings` unless the user says otherwise.
- The default database is SQLite at `db.sqlite3`.
- `DEBUG = True` in current settings; do not treat this repo as production-ready.

## Primary Commands
- Start dev server: `.venv/bin/python manage.py runserver`
- Run Django system checks: `.venv/bin/python manage.py check`
- Apply migrations: `.venv/bin/python manage.py migrate`
- Create migrations: `.venv/bin/python manage.py makemigrations`
- Open Django shell: `.venv/bin/python manage.py shell`
- Collect static files if needed: `.venv/bin/python manage.py collectstatic`

## Build Commands
- There is currently no separate build toolchain configured.
- For this repo, the closest equivalent to a build verification step is: `.venv/bin/python manage.py check`
- If static assets, packaging, or frontend tooling are added later, update this section with the exact commands.

## Lint Commands
- There is currently no configured linter in the repository.
- No `pyproject.toml`, `ruff.toml`, `mypy.ini`, `setup.cfg`, `.flake8`, or ESLint/Prettier config was found.
- Do not invent `ruff`, `black`, `flake8`, or `mypy` commands as required checks unless the user explicitly asks for them.
- If you add lint tooling in the future, document the exact invocation here.

## Test Commands
- Run all tests: `.venv/bin/python manage.py test`
- Current observed result: the command runs successfully but reports `0` tests.
- Django test discovery should be the default mechanism unless the repo later adopts `pytest`.

## Single-Test Commands
- Run one test module: `.venv/bin/python manage.py test path.to.tests`
- Run one test class: `.venv/bin/python manage.py test path.to.tests.MyTestCase`
- Run one test method: `.venv/bin/python manage.py test path.to.tests.MyTestCase.test_method`
- Example module form: `.venv/bin/python manage.py test myapp.tests`
- Example class form: `.venv/bin/python manage.py test myapp.tests.SettingsTests`
- Example method form: `.venv/bin/python manage.py test myapp.tests.SettingsTests.test_debug_default`
- If an app is later added with a `tests.py` file, use that dotted module path.
- Prefer the narrowest test target that covers the change you made.

## Verification Expectations
- Minimum verification for configuration-only changes: `.venv/bin/python manage.py check`
- Minimum verification for behavior changes: `.venv/bin/python manage.py test`
- If you add or modify migrations, also run: `.venv/bin/python manage.py makemigrations --check`
- If a command cannot be run locally, say so explicitly in your final response.

## Code Style Overview
- Match the existing Django-generated project style unless the repo adopts stricter tooling later.
- Keep changes minimal and local.
- Prefer straightforward Django conventions over custom abstractions.
- Use 4-space indentation.
- Keep lines reasonably short and readable; no exact formatter-enforced width is configured.
- Use ASCII unless a file already requires Unicode.

## Imports
- Group imports in this order: standard library, third-party, local application imports.
- Separate import groups with a blank line.
- Prefer explicit imports over wildcard imports.
- Keep import style consistent with current files, for example `from pathlib import Path`.
- Remove unused imports when touching a file.

## Formatting
- Follow existing spacing and blank-line patterns in `manage.py` and `config/*.py`.
- Preserve concise module docstrings where Django generated them.
- Do not reformat unrelated files just to satisfy a personal preference.
- Avoid adding comments for obvious code.
- Add a short comment only when logic is non-obvious.

## Types
- There is currently no type-checking configuration in the repository.
- Do not introduce large-scale type annotation churn into generated Django files.
- For new non-trivial functions, add type hints when they improve clarity.
- Prefer simple built-in typing syntax on Python 3.12, for example `list[str]`.
- Keep type usage consistent within the file you are editing.

## Naming Conventions
- Use `snake_case` for functions, variables, and module names.
- Use `PascalCase` for classes.
- Use `UPPER_SNAKE_CASE` for module-level constants and Django settings.
- Name Django apps, modules, URLs, and settings according to normal Django conventions.
- Prefer descriptive names over abbreviations unless the abbreviation is already standard in Django.

## Django Conventions
- Keep configuration in `config/settings.py` unless there is a clear reason to split settings.
- Register new URLs in `config/urls.py` or include app-specific URLconfs once apps exist.
- Use Django management commands instead of ad hoc scripts when an equivalent command exists.
- Prefer framework defaults before adding custom infrastructure.
- If creating a new app, use Django's standard layout and register it in `INSTALLED_APPS`.

## Error Handling
- Raise specific exceptions instead of broad `Exception` where practical.
- Preserve exception chaining when re-raising, as seen in `manage.py` using `raise ... from exc`.
- Fail loudly on configuration errors rather than hiding them.
- Do not swallow exceptions without a concrete reason.
- User-facing messages should be clear and actionable.

## Testing Guidance
- Add focused tests with behavior changes.
- Prefer Django's built-in test framework unless the repo formally adopts another runner.
- Keep tests close to the app they cover.
- When adding a regression test, name it after the behavior or bug being protected.
- Run the smallest relevant test target first, then broader coverage if needed.

## Change Discipline For Agents
- Read the surrounding file before editing.
- Do not assume tooling exists if it is not configured in the repo.
- Do not add new dependencies without a clear need.
- Do not rewrite generated Django files without a reason tied to the task.
- Do not modify unrelated files in the same change.
- Keep commits and diffs easy to review.

## Repository-Specific Notes
- This repository currently looks like a freshly generated Django project.
- Existing code uses single-quoted strings in Python files; preserve that style in touched files.
- Existing files are lightly structured and mostly framework-generated; match that simplicity.
- Since no dedicated lint or format config exists, consistency with neighboring code matters more than external style defaults.

## When Updating This File
- Prefer facts verified from the repository over generic advice.
- Add exact commands, not approximate descriptions.
- If Cursor or Copilot rule files are added later, summarize their actionable rules here.
- Keep this file synchronized with actual tooling and project structure.
