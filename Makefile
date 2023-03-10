hello:
	@echo "Welcome to Repo Automator. Please include a command after the make"

venv:
	python -m venv venv

m:
	python manage.py migrate

mm:
	python manage.py makemigrations

install:
	pip install -r requirements.txt

run:
	python manage.py runserver

build:
	docker compose --project-name repo_automator build

start:
	docker compose --project-name repo_automator up

start_d:
	docker compose --project-name repo_automator up -d

down:
	docker compose --project-name repo_automator down -v

lints:
	flake8 . --config=setup.cfg
	black .
	pylint --recursive=y .
	isort --profile black .
	docformatter . --recursive --check

checks:
	python manage.py test
	flake8 . --config=setup.cfg
	isort --check-only --profile black .
	pylint . --recursive=y --rcfile=.pylintrc
	docformatter . --recursive --check
	black --check --diff .

test:
	python manage.py test
