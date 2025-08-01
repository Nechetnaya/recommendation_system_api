"""
This module provides the core recommendation logic for generating personalized post
recommendations based on user features and a trained CatBoost model.

Functions:

- get_user_df(user_id: int, time: datetime) -> pd.DataFrame:
    Constructs a feature-enriched DataFrame of posts for a given user.
    Filters out posts the user has already interacted with (liked).
    Adds user-related time features (hour and weekday).
    Returns:
        pd.DataFrame: Feature matrix combining user and post features.

- get_recommend_ids(user_id: int, time: datetime, model: CatBoostClassifier, limit: int = 5) -> list:
    Generates a ranked list of post IDs recommended for the given user.
    Scores posts using the provided CatBoost model based on user-post features.
    Returns:
        list: Top-N recommended post IDs, ranked by predicted relevance.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from catboost import CatBoostClassifier

import app.core.state as state
from app.core.features_loader import load_likes_list

def get_user_df(user_id: int, time: datetime) -> pd.DataFrame:
    user_row = state.users_data[state.users_data['user_id'] == user_id]
    if user_row.empty:
        return pd.DataFrame()

    user_data = user_row.drop('user_id', axis=1).iloc[0].to_dict()
    user_data['hour'] = np.float32(time.hour)
    user_data['weekday'] = np.float32(time.weekday())

    posts_list = load_likes_list(user_id, time)
    if not posts_list:
        post_subset = state.posts_data
    else:
        posts_to_exclude = set(posts_list)
        post_subset = state.posts_data.loc[~state.posts_data['post_id'].isin(posts_to_exclude)]

    post_indexed = post_subset.set_index('post_id')
    user_features_df = pd.DataFrame([user_data] * len(post_indexed), index=post_indexed.index)
    df = pd.concat([post_indexed, user_features_df], axis=1)

    return df


def get_recommend_ids(user_id: int, time: datetime, model: CatBoostClassifier, limit: int = 5) -> list:
    df = get_user_df(user_id, time)
    if df.empty:
        return []

    features = model.feature_names_
    df['pred'] = model.predict_proba(df[features])[:, 1]

    return df.nlargest(limit, 'pred').index.tolist()
