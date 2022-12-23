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
	docker-compose build

start:
	docker-compose up

lints:
	flake8 . --config=setup.cfg
	black --check --diff .
	pylint --recursive=y .
	isort --check-only .
	docformatter . --recursive --check

test:
	python manage.py test
