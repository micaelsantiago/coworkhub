.PHONY: setup up down logs shell test lint format makemigrations migrate

setup:
	cp -n .env.example .env || true
	docker compose build

up:
	docker compose up

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec web python manage.py shell

test:
	docker compose run --rm web pytest

lint:
	docker compose run --rm web ruff check .
	docker compose run --rm web ruff format --check .

format:
	docker compose run --rm web ruff check --fix .
	docker compose run --rm web ruff format .

makemigrations:
	docker compose run --rm web python manage.py makemigrations

migrate:
	docker compose run --rm web python manage.py migrate
