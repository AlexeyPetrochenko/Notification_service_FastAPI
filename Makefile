run_tests:
	python3 -m pytest .

lint:
	flake8 .e

types:
	mypy .

campaign_worker:
	python3 -m app.workers.campaign_worker

uv_run_app:
	uv run fastapi dev