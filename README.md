# Interstellar Route Planner

A Django-based route planner for interstellar travel using shortest-path algorithms.

## Run with Docker (steps)

Prerequisite: Install Docker Desktop.

1. Copy env file:
	- `cp .env.docker.example .env.docker`

2. Start services:
	- `docker-compose up --build`
	- Wait for migrations and sample data to load

3. Open the app:
	- http://localhost:8000

4. Stop services:
	- `docker-compose down` (add `-v` to drop the db volume)

## Run locally (no Docker)

Prerequisites: Python 3.11, PostgreSQL running locally, `pipenv` installed (`pip install pipenv`).

1. Copy env file: `cp .env.docker.example .env`
2. Install dependencies (creates venv): `pipenv install --dev`
3. Prepare DB: `pipenv run python manage.py migrate`
4. Load sample data: `pipenv run python manage.py loaddata initial_gates`
5. Start app: `pipenv run python manage.py runserver`
6. Open: http://localhost:8000
