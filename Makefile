.PHONY: start app

start:
	python -m uvicorn app.main:app --reload

app:
	python -m app.main

test:
	python tests/test_api.py

test_noid:
	python tests/test_api_noid.py

