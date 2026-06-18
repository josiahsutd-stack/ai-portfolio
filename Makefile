.PHONY: setup sample-data test lint format smoke health demo clean run-portfolio

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

smoke:
	python scripts/run_smoke_tests.py

health:
	python scripts/check_repo_health.py

demo:
	streamlit run projects/$(PROJECT)/app.py

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','.ruff_cache']]"

run-portfolio:
	python -m http.server 8080 --directory portfolio-site
