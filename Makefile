run_tests:
	python3 -m pytest .

linters:
	flake8 .e

types:
	mypy .

campaign_worker:
	python3 -m app.workers.campaign_worker
