PYTHON ?= python

.PHONY: setup verify sample-data test lint format smoke health claims evidence provenance site review-artifacts demo clean run-portfolio

setup:
	$(PYTHON) scripts/setup.py

verify:
	$(PYTHON) scripts/verify.py

sample-data:
	$(PYTHON) scripts/generate_sample_data.py

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check --fix .

smoke:
	$(PYTHON) scripts/run_smoke_tests.py

health:
	$(PYTHON) scripts/check_repo_health.py

claims:
	$(PYTHON) scripts/check_claims.py

evidence:
	$(PYTHON) scripts/check_evidence_claims.py

provenance:
	$(PYTHON) experiments/real-model-finetune-lab/scripts/build_uci_sms_subset.py --check

site:
	$(PYTHON) scripts/check_portfolio_site.py

review-artifacts:
	$(PYTHON) scripts/generate_review_artifacts.py

demo:
	streamlit run projects/$(PROJECT)/app.py

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','.ruff_cache']]"

run-portfolio:
	$(PYTHON) -m http.server 8080 --directory portfolio-site
