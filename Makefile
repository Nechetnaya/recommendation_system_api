# Makefile for managing app lifecycle and training pipeline
# Usage:
#   make start          # Run app with auto-reload (development)
#   make check          # Run course checker app with auto-reload
#   make app            # Run app without reload
#   make test           # Run tests
#   make build          # Build Docker image
#   make run            # Run Docker container with ports 8000 and 6432 exposed
#   make make-features  # Generate features dataset for training
#   make train-model    # Train model with new data from database
#   make save-features  # Save features for users and posts into DB
#   make ab             # Run A/B test script

.PHONY: start app check test build run make-features train-model save-features ab

# run app with reload
start:
	python -m uvicorn app.main:app --reload

# run check for course
check:
	python -m uvicorn app.app_for_course_checker_ab:app --reload

# run app
app:
	python -m app.main

# test app
test:
	python -m pytest tests

# build docker
build:
	docker build --platform=linux/amd64 -t recommend-app .

# run docker
run:
	docker run -it -p 8000:8000 -p 6432:6432 recommend-app

# make feature for training
make-features:
	python -m recommender.features.build_train_dataset

# train model with new data from db
train-model:
	python -m recommender.training.train_model_entry

# make features for users and posts
save-features:
	python -m recommender.features.save_features_to_db

# run A/B test script
ab:
	python -m ab_test.ab_test_script
