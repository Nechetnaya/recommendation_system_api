"""
This module provides utility functions to load data from a PostgreSQL database
using SQL queries, including user and post features, user likes, and top-liked posts.

Functions:

- batch_load_sql(query: str) -> pd.DataFrame:
    Loads a large SQL query result in chunks and concatenates them into a single DataFrame.
    Useful for memory-efficient loading of large tables.

- load_features(name: str) -> pd.DataFrame:
    Loads predefined feature tables for users or posts based on the `name` argument.
    Raises ValueError if an unknown name is provided.

- load_likes_list(user_id: int, time: datetime) -> list:
    Returns a list of post IDs that the user has liked before a given timestamp.

- select_top_liked_posts_ids(limit: int) -> list:
    Returns a list of post IDs with the highest number of likes, limited by `limit`.

Requirements:
- Expects tables: `nechetnaya_user_features_full_1507`,
  `nechetnaya_post_features_full_1507`, `nechetnaya_likes`, `feed_data`.
"""

from datetime import datetime
import pandas as pd
from app.db.database import engine


def batch_load_sql(query: str) -> pd.DataFrame:
    CHUNKSIZE = 50000
    chunks = []
    with engine.connect().execution_options(stream_results=True) as conn:
        for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
            chunks.append(chunk_dataframe)
    return pd.concat(chunks, ignore_index=True)


def load_features(name: str) -> pd.DataFrame:
    queries = {
        'users': "SELECT * FROM nechetnaya_user_features_full_1507",
        'posts': "SELECT * FROM nechetnaya_post_features_full_1507",
    }
    if name not in queries:
        raise ValueError(f"Unknown dataset name: {name}")
    return batch_load_sql(queries[name])


def load_likes_list(user_id: int, time: datetime) -> list:
    query = """
    SELECT post_id
    FROM nechetnaya_likes
    WHERE user_id = %(user_id)s
      AND timestamp < %(time)s
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"user_id": user_id, "time": time})

    return df['post_id'].tolist()


def select_top_liked_posts_ids(limit: int) -> list:
    query = """
    SELECT post_id, COUNT(*) as likes
    FROM feed_data
    WHERE target = 1
    GROUP BY post_id
    ORDER BY likes DESC
    LIMIT %(limit)s
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"limit": limit})
    return df['post_id'].tolist()

