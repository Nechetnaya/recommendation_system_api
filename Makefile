.PHONY: start app

# run app with reload
start:
	python -m uvicorn app.main:app --reload

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
	python -m recommender/features/build_train_dataset.py

# train model with new data fom db
train-model:
	python -m recommender.training.train_model_entry

# make features for users and posts
save-features:
	python recommender/features/save_features_to_db.py
