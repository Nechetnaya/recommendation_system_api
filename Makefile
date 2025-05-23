.PHONY: start app

start:
	python -m uvicorn app.main:app --reload

app:
	python -m app.main

test:
	python -m pytest tests

build:
	docker build --platform=linux/amd64 -t recommend-app .

run:
	docker run -it -p 8000:8000 -p 6432:6432 recommend-app

