FROM node:24-alpine AS frontend

WORKDIR /frontend
COPY package.json package-lock.json ./
RUN npm ci
COPY assets ./assets
COPY templates ./templates
COPY apps ./apps
RUN npm run build

FROM python:3.13-slim AS runtime

ARG LOCAL_UID=1000
ARG LOCAL_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --gid "${LOCAL_GID}" django \
    && adduser --disabled-password --gecos "" --uid "${LOCAL_UID}" --gid "${LOCAL_GID}" django

COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[dev]"

COPY . .
COPY --from=frontend /frontend/static/css/app.css ./static/css/app.css
COPY --from=frontend /frontend/static/js/app.js ./static/js/app.js

RUN chmod +x /app/scripts/*.sh \
    && chown -R django:django /app

USER django

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
