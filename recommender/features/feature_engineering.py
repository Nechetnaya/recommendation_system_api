import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from lightfm import LightFM
from lightfm.data import Dataset

from app.db.database import engine

# USERS FEATURES
# load users data
def get_user_data():
    with engine.connect() as conn:
        return pd.read_sql('SELECT * FROM public.user_data', conn)

# count users mean views per day (users activity rate)
def get_user_activity_features():
    query = """
    WITH preagg AS (
        SELECT user_id, COUNT(target) AS views_count,
               MAX("timestamp")::date - MIN("timestamp")::date AS active_days
        FROM public.feed_data
        WHERE action = 'view'
        GROUP BY user_id
    )
    SELECT user_id, views_count / NULLIF(active_days, 0) AS views_day FROM preagg
    """
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_user_embeddings():
    _, _, user_df_fm, _ = get_lightfm_embeddings()
    return user_df_fm


# count users' likes-rate fot post's topics
def get_user_topic_preferences():
    query = """
    SELECT 
        user_id,     
        SUM(target) FILTER (where topic = 'movie')::decimal / COUNT(post_id) FILTER (where topic = 'movie') AS movie_likes_rate,
        COUNT(post_id) FILTER (where topic = 'movie')::decimal / COUNT(post_id) AS movie_views_rate,  
        
        SUM(target) FILTER (where topic = 'business')::decimal / COUNT(post_id) FILTER (where topic = 'business') AS business_likes_rate,
       
        SUM(target) FILTER (where topic = 'covid')::decimal / COUNT(post_id) FILTER (where topic = 'covid') AS covid_likes_rate,
    
        SUM(target) FILTER (where topic = 'sport')::decimal / COUNT(post_id) FILTER (where topic = 'sport') AS sport_likes_rate,
        
        SUM(target) FILTER (where topic = 'politics')::decimal / COUNT(post_id) FILTER (where topic = 'politics') AS politics_likes_rate,
        
        SUM(target) FILTER (where topic = 'tech')::decimal / COUNT(post_id) FILTER (where topic = 'tech') AS tech_likes_rate
    
    FROM public.feed_data f LEFT JOIN public.post_text_df p USING (post_id)
    WHERE action = 'view'
    GROUP BY user_id
    """

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def make_user_features():
    base = get_user_data()
    activity = get_user_activity_features()
    preferences = get_user_topic_preferences()
    embeddings = get_user_embeddings()

    user_df = base.merge(activity, on='user_id', how='left')\
                   .merge(preferences, on='user_id', how='left')\
                   .merge(embeddings, on='user_id', how='left').fillna(0)

    bins = [13, 19, 24, 33, 50, 95]
    labels = ['14-19', '20-24', '25-33', '34-50', '51+']
    user_df['age_group'] = pd.cut(user_df['age'], bins=bins, labels=labels, right=True)
    return user_df.drop(columns='age')


# POST FEATURES
# load posts data
def get_post_data():
    with engine.connect() as conn:
        return pd.read_sql('SELECT post_id, text, topic FROM public.post_text_df', conn)

#select most popular posts for recommendations
def get_popular_post_ids(min_likes=2000):
    query = """
    SELECT post_id, COUNT(*) AS likes
    FROM feed_data
    WHERE action = 'view'
    GROUP BY post_id
    HAVING COUNT(*) > %(min_likes)s
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"min_likes": min_likes})
    return df['post_id'].tolist()

# create features from posts text with TF-IDF and SVD
def get_text_features(posts_df):
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    svd = TruncatedSVD(n_components=10)
    X = vectorizer.fit_transform(posts_df['text'])
    X_reduced = svd.fit_transform(X)
    return pd.DataFrame(X_reduced, columns=[f'tfidf_{i}' for i in range(X_reduced.shape[1])])


def get_post_rating():
    query = """
    SELECT 
        post_id,
        DENSE_RANK() OVER (ORDER BY likes DESC) AS likes_rating
    FROM
    (
        SELECT post_id, SUM(target) AS likes, COUNT(target) AS views 
        FROM feed_data
        WHERE action = 'view'
        GROUP BY post_id
    ) AS t
    """
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_post_embeddings():
    _, _, _, post_df_fm = get_lightfm_embeddings()
    return post_df_fm


def make_post_features():
    posts = get_post_data()
    ids = get_popular_post_ids()
    posts = posts[posts['post_id'].isin(ids)]

    tfidf_df = get_text_features(posts)
    rating = get_post_rating()
    embeddings = get_post_embeddings()

    post_df = pd.concat([posts.reset_index(drop=True), tfidf_df], axis=1)
    post_df = post_df.merge(rating, on='post_id', how='left') \
        .merge(embeddings, on='post_id', how='left').fillna(0)

    return post_df.drop(columns='text')


# LIGHTFM FEATURES
def get_lightfm_embeddings():
    query = 'SELECT post_id, user_id FROM public.feed_data WHERE target = 1'
    chunks = []
    with engine.connect() as conn:
        for chunk in pd.read_sql(query, conn, chunksize=100_000):
            chunks.append(chunk)
    df = pd.concat(chunks)

    dataset = Dataset()
    dataset.fit(df['user_id'], df['post_id'])
    interactions, _ = dataset.build_interactions(list(zip(df['user_id'], df['post_id'])))

    model = LightFM(loss='warp')
    model.fit(interactions, epochs=10, num_threads=2)

    user_embeddings = model.get_user_representations()[1]
    item_embeddings = model.get_item_representations()[1]

    user_id_map, _, post_id_map, _ = dataset.mapping()
    user_inv = {v: k for k, v in user_id_map.items()}
    post_inv = {v: k for k, v in post_id_map.items()}

    user_df = pd.DataFrame(user_embeddings)
    user_df['internal_id'] = user_df.index
    user_df['user_id'] = user_df['internal_id'].map(user_inv)
    user_df = user_df.drop(columns='internal_id')
    user_df = user_df.rename(columns={i: f'user_emb_{i}' for i in range(user_embeddings.shape[1])})

    post_df = pd.DataFrame(item_embeddings)
    post_df['internal_id'] = post_df.index
    post_df['post_id'] = post_df['internal_id'].map(post_inv)
    post_df = post_df.drop(columns='internal_id')
    post_df = post_df.rename(columns={i: f'post_emb_{i}' for i in range(item_embeddings.shape[1])})

    return dataset, model, user_df, post_df




