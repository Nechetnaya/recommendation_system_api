import pandas as pd

from recommender.build_train_dataset import load_train_dataset
from recommender.model import train_and_save_model

if __name__ == "__main__":
    df = load_train_dataset()
    cat_features = ['topic', 'country', 'exp_group', 'age_group']
    train_and_save_model(df, cat_features)
