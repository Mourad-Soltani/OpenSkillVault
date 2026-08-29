# OpenSkillVault Makefile
# Author: Mourad.Soltani

.PHONY: install run test health clean

install:
	pip install -r requirements.txt

run:
	cd backend && python app.py

test:
	pytest -v

health:
	curl -s http://localhost:5000/health | python -m json.tool

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov

# Signature: Mourad.Soltani
