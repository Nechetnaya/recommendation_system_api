import pandas as pd
from datetime import datetime
from catboost import Pool

import app.core.state as state
from app.core.features_loader import load_likes_list


def get_user_df(user_id: int, time: datetime) -> pd.DataFrame:
    user_row = state.users_data[state.users_data['user_id'] == user_id]
    if user_row.empty:
        return pd.DataFrame()

    user_data = user_row.drop(columns='user_id').iloc[0]
    posts_list = load_likes_list(user_id, time)

    if not posts_list:
        return state.posts_data.set_index('post_id').assign(**user_data.to_dict())

    posts_to_exclude = set(posts_list)
    posts_subset = state.posts_data.loc[~state.posts_data['post_id'].isin(posts_to_exclude)]

    return posts_subset.set_index('post_id').assign(**user_data.to_dict())


def get_recommend_ids(user_id: int, time: datetime, limit: int = 5) -> list:
    df = get_user_df(user_id, time)
    if df.empty:
        return []

    pool = Pool(df, cat_features=state.CAT_FEATURES)
    df['pred'] = state.model.predict_proba(pool)[:, 1]

    return df.nlargest(limit, 'pred').index.tolist()
