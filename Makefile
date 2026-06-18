.PHONY: setup sample-data test lint format run-portfolio

setup:
	python -m venv .venv
	.venv/Scripts/python -m pip install --upgrade pip
	.venv/Scripts/python -m pip install -r requirements.txt -r requirements-dev.txt

sample-data:
	python scripts/generate_sample_data.py

test:
	pytest

lint:
	ruff check .

format:
	black .
	ruff check --fix .

run-portfolio:
	python -m http.server 8080 --directory portfolio-site

