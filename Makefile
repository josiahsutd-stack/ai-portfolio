PYTHON ?= python

.PHONY: setup verify review sample-data test lint format smoke health claims commands profile visual-contract evidence provenance site visuals review-artifacts demo clean run-portfolio

setup:
	$(PYTHON) scripts/setup.py

verify:
	$(PYTHON) scripts/verify.py

review:
	$(PYTHON) scripts/reviewer_check.py

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

commands:
	$(PYTHON) scripts/check_documented_commands.py

profile:
	$(PYTHON) scripts/check_profile_readme.py

visual-contract:
	$(PYTHON) scripts/check_visual_contract.py

evidence:
	$(PYTHON) scripts/check_evidence_claims.py

provenance:
	$(PYTHON) experiments/local-text-classification-lab/scripts/build_uci_sms_subset.py --check

site:
	$(PYTHON) scripts/check_portfolio_site.py

visuals:
	$(PYTHON) scripts/generate_system_maps.py

review-artifacts:
	$(PYTHON) scripts/generate_review_artifacts.py

demo:
	streamlit run projects/$(PROJECT)/app.py

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','.ruff_cache']]"

run-portfolio:
	$(PYTHON) -m http.server 8080 --directory portfolio-site
