"""
Module for generating and saving training dataset for the recommendation model.

Functions:
- load_feed_data(popular_post_ids, limit=..., chunk_size=...):
    Loads filtered and deduplicated feed data for selected post IDs from the database.

- make_train_dataset():
    Combines user, post, and interaction features into a single training dataset.

- save_train_dataset(path):
    Saves the generated training dataset to a parquet file.

- load_train_dataset(path):
    Loads the training dataset from a parquet file.
"""

import pandas as pd
from pathlib import Path

from app.db.database import engine
from recommender.features.feature_engineering import make_user_features, make_post_features



def load_feed_data(popular_post_ids, limit=2_000_000, chunk_size=500_000):
    post_ids_str = ','.join(map(str, popular_post_ids))
    query = f"""
        SELECT timestamp, post_id, user_id, target
        FROM public.feed_data
        WHERE action = 'view' AND post_id IN ({post_ids_str})
        ORDER BY timestamp
        LIMIT {limit}
    """
    chunks = []
    with engine.connect() as conn:
        for chunk in pd.read_sql(query, conn, chunksize=chunk_size):
            chunks.append(chunk)
    feed_df = pd.concat(chunks, ignore_index=True)
    feed_df = (
        feed_df.sort_values(by="target", ascending=False)
        .drop_duplicates(subset=["user_id", "post_id"], keep="first")
        .sort_values(by="timestamp")
    )
    return feed_df


def make_train_dataset() -> pd.DataFrame:
    user_df = make_user_features()
    post_df = make_post_features()
    popular_post_ids = post_df['post_id'].tolist()
    feed_df = load_feed_data(popular_post_ids)

    train_df = (
        feed_df
        .merge(post_df, how="left", on="post_id")
        .merge(user_df, how="left", on="user_id")
        .set_index(["timestamp", "user_id", "post_id"])
    )

    return train_df

def save_train_dataset(path: str = "recommender/train_data/train_dataset.parquet"):
    df = make_train_dataset()
    df.to_parquet(path)
    print(f"Train dataset saved to {path}")


def load_train_dataset(path: str = "recommender/train_data/train_dataset.parquet") -> pd.DataFrame:
    return pd.read_parquet(Path(path))


if __name__ == "__main__":
    save_train_dataset()
