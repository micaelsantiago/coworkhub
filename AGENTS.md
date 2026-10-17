# Repository guide

## Current state

- This is a Docker-first Django 5.2 monolith; Python 3.13 dependencies are installed in the image rather than a checked-in virtualenv.
- The domain apps under `apps/` are mostly placeholders. Currently implemented behavior is limited to the email-based custom `accounts.User`, health/readiness probes, and the starter UI. Treat `docs/` as the target design, not proof that a feature exists.
- For product or domain work, read `docs/mvp.md` and `docs/dominio.md`. For app boundaries and implementation constraints, read `docs/arquitetura.md`; its examples include planned code that is not yet present.

## Local workflow

- Before creating a branch, opening a PR, merging, or deleting a branch, read `docs/fluxo-de-desenvolvimento.md`. Work branches always start from `main`, validate through `develop`, and are promoted independently to `main`.
- Run `make setup` first: Compose requires `.env`, and this copies `.env.example` when absent before building images. `make up` starts PostgreSQL, Redis, Django, Celery worker/beat, and the frontend watcher; the web startup script applies migrations automatically.
- Full verification is `make lint` followed by `make test`.
- Focus a test without running the suite: `docker compose run --rm web pytest tests/test_user.py::test_user_authenticates_with_email` (replace the node path as needed). Pytest always uses `config.settings.test` via `pyproject.toml`.
- Generate and apply migrations with `make makemigrations` and `make migrate`. Commit migration files with model changes.
- Frontend sources are `assets/css/input.css` and `assets/js/app.js`; `static/css/app.css` and `static/js/app.js` are generated and ignored. Build once with `docker compose run --rm frontend sh -c "npm ci && npm run build"`; `make up` runs both watchers.

## Architecture constraints

- Keep this server-rendered: Django templates + HTMX responses, with Alpine.js only for small client interactions; there is no separate SPA/API in the current architecture.
- Put use-case coordination in an app's `services.py`, complex reads in `selectors.py`, and request orchestration in views. Enforce business integrity in backend forms/services and PostgreSQL constraints, not only in HTMX/Alpine behavior.
- Before implementing tenant-aware models, queries, middleware, tasks, or tests, read `docs/arquitetura.md` sections 4–5. The required design is fail-closed tenant scoping, explicit tenant context in Celery tasks, database-level cross-tenant protection, and isolation tests; none of that foundation is implemented yet.
- `platform_billing` is the Coworkhub-to-tenant SaaS subscription; `member_billing` is the coworking's billing of its members. Keep these domains separate.
- Add environment variables to `.env.example`; `.env` is ignored. Settings belong in the appropriate `config/settings/{base,dev,test,prod}.py` layer.
