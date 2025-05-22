#import psutil
from datetime import datetime
# import uvicorn
from typing import List
from fastapi import FastAPI, Depends

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import os
from catboost import CatBoostClassifier, Pool
import pandas as pd

#from src.schema import PostGet
from schema import PostGet


# process = psutil.Process(os.getpid())

# load model
def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":  # проверяем где выполняется код в лмс, или локально. Немного магии
        MODEL_PATH = '/workdir/user_input/model'
    else:
        MODEL_PATH = path
    return MODEL_PATH


def load_models():
    model_path = get_model_path("src/best_model_14_05")
    model = CatBoostClassifier()
    model.load_model(model_path)
    return model


# load dataframes for model
def batch_load_sql(query: str) -> pd.DataFrame:
    CHUNKSIZE = 100000
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)


def load_features(name: str) -> pd.DataFrame:
    if name == 'users':
        query = """
        SELECT * FROM irina_nechetnaya_user_df_for_best_model_14_05
        """
    elif name == 'posts':
        query = """
        SELECT * FROM irina_nechetnaya_post_df_for_best_model_14_05
        """
    elif name == 'views':
        query = """
        SELECT * FROM irina_nechetnaya_viewed_pop_posts
        """
    else:
        raise ValueError(f"Unknown dataset name: {name}")

    return batch_load_sql(query)


# get dataframe for user
def get_user_df(
    id: int,
    users_df: pd.DataFrame,
    posts_df: pd.DataFrame,
    views_df: pd.DataFrame
) -> pd.DataFrame:

    user_data = users_df[users_df['user_id'] == id].drop('user_id', axis=1).iloc[0]
    posts_list = views_df.set_index('user_id').loc[id, 'post_ids']
    posts_data = posts_df[posts_df['post_id'].isin(posts_list)].set_index('post_id')
    df_user = posts_data.assign(**user_data.to_dict())

    return df_user

# get predictions and recommended posts
def get_recomend_ids(
    id: int,
    users_df: pd.DataFrame,
    posts_df: pd.DataFrame,
    views_df: pd.DataFrame,
    cat_features: list
) -> list:

    df = get_user_df(id, users_df, posts_df, views_df)
    pool = Pool(df, cat_features=cat_features)

    pred = data_cache['model'].predict_proba(pool)[:, 1]

    return (
        pd.DataFrame({'post_id': df.index, 'pred': pred})
        .sort_values('pred', ascending=False)
        .head(5)
        .post_id
        .to_list()
        )


app = FastAPI()

engine = create_engine(
    "postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
    "postgres.lab.karpov.courses:6432/startml",
    pool_size = 10,
    max_overflow = 20,
    pool_timeout = 30
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)


# connection to startml
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

data_cache = {
    'CAT_FEATURES': ['topic', 'country', 'exp_group', 'age_group'],
}

@app.on_event('startup')
def load_data():
    # start_mem = process.memory_info().rss / 1024 / 1024
    data_cache['users_data'] = load_features('users')
    data_cache['posts_data'] = load_features('posts')
    data_cache['views_data'] = load_features('views')
    data_cache['model'] = load_models()
    # end_mem = process.memory_info().rss / 1024 / 1024
    # print(start_mem, end_mem, end_mem - start_mem)


@app.get("/post/recommendations/", response_model=List[PostGet])
def recommended_posts(
    id: int,
    time: datetime,
    limit: int = 5,
    db: Session = Depends(get_db)
) -> List[PostGet]:
    # start_mem = process.memory_info().rss / 1024 / 1024
    posts_list = get_recomend_ids(
        id,
        data_cache['users_data'],
        data_cache['posts_data'],
        data_cache['views_data'],
        data_cache['CAT_FEATURES']
    )
    result = db.query(Post).filter(Post.id.in_(posts_list)).all()
    # end_mem = process.memory_info().rss / 1024 / 1024
    # mem_diff = end_mem - start_mem
    # print(end_mem, mem_diff)
    return result
