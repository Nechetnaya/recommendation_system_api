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
        'users': "SELECT * FROM irina_nechetnaya_user_df_for_cb_fm_full_model_20_05",
        'posts': "SELECT * FROM irina_nechetnaya_post_df_for_cb_fm_full_model_20_05",
    }
    if name not in queries:
        raise ValueError(f"Unknown dataset name: {name}")
    return batch_load_sql(queries[name])


def load_likes_list(user_id: int, time: datetime) -> list:
    query = """
    SELECT post_id
    FROM irina_nechetnaya_likes
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

