# Recommendation System API

Content recommender system built with FastAPI and CatBoost, using user behavior, post text, and LightGCN embeddings.  
Developed as a pet project to learn top-N recommendation modeling, A/B testing, and API integration.

This project includes two recommendation models with different feature sets and a full A/B test pipeline to compare their performance on held-out data.

---

## Project Description

###  Data:
- Feed log: 76 million user interaction rows collected over 3 months from 2021-10-01 to 2021-12-31  
- Data on 163K users and 7K posts  
- Stored in PostgreSQL (accessed via Redash)

### Feed data fields:
| Field name | Overview                                                                                      |
|------------|-----------------------------------------------------------------------------------------------|
| `timestamp` | Time when the view happened                                                                 |
| `user_id`   | ID of the user who performed the action                                                     |
| `post_id`   | ID of the post that was viewed                                                              |
| `action`    | Type of action: view or like                                                                |

### User data fields:
| Field name | Overview                                         |
|------------|--------------------------------------------------|
| `age`      | User age (from profile)                          |
| `city`     | User city (from profile)                         |
| `country`  | User country (from profile)                      |
| `exp_group`| Experimental group: an encrypted category       |
| `gender`   | User gender                                      |
| `user_id`  | Unique user identifier                           |
| `os`       | Operating system of the device                   |
| `source`   | Whether the user came from organic traffic or ads|

### Post data fields:
| Field name | Overview                 |
|------------|--------------------------|
| `id`       | Unique post identifier   |
| `text`     | Text content of the post |
| `topic`    | Main topic of the post   |

### Goal:
- Build a model to predict the probability that a user will like a post  
- Implement a service returning the top N posts ranked by this probability

### Completed:
- Preprocessing and feature engineering done in notebooks  
- User and post embeddings generated with LightGCN  
- Text features extracted from posts (TFIDF + TruncatedSVD)  
- Two CatBoost models trained: baseline and extended with extra features  
- Integrated into FastAPI app with PostgreSQL connection  
- A/B test implemented to compare models on held-out data  
- Recommendation API filters out already liked posts

### A/B Test Methodology
An A/B test was conducted on held-out user interactions from December 2021 to compare the two recommendation models:

- **Control group** received recommendations from the baseline model (fewer features)  
- **Test group** received recommendations from the enhanced model (with topic-level like rates, lexical features, and LightGCN embeddings)

**Evaluation metrics:**
- `HitRate@5`: checks whether at least one liked post is present in the top-5 recommended

Each user was deterministically assigned to an experiment group using a hash function on their user ID to simulate real-life A/B testing.

Full analysis in notebook:  
📄 `ab_test/ab_test_analysis.ipynb`

### Results:
| Metric         | Control Model | Test Model |
|----------------|---------------|------------|
| AUC            | 0.773         | **0.82**   |
| HitRate@5      | 0.611         | **0.706**  |

---

## Feature Description

### User features:
- `weekday`, `hour` – weekday and hour of the request  
- `gender`, `age` – from profile  
- `avg_log_word_len`, `max_log_word_len` – lexical stats of previously liked posts  
- Topic-specific like rates: `movie_likes_rate`, `business_likes_rate`, `covid_likes_rate`, `sport_likes_rate`, `politics_likes_rate`, `tech_likes_rate`  
- `views_per_day`, `likes_per_day` – user activity stats  
- One-hot encoded country: e.g., `country_Belarus`, ..., `country_Ukraine`  
- Experiment groups: `exp_group_1`, ..., `exp_group_4`  
- `city_freq` – frequency of city occurrence

### Post features:
- `log_text_len`, `n_words`, `avg_word_len` – lexical features  
- `like_count_log`, `like_rank`, `like_score` – popularity features  
- `tfidf_0` to `tfidf_99` – TFIDF vectors reduced by Truncated SVD  
- `topic_*` – one-hot encoded topics  
- `item_emb_0` to `item_emb_63` – LightGCN embeddings

---

## Technology stack

- Python 3.8  
- FastAPI  
- CatBoost  
- SQLAlchemy + PostgreSQL  
- Pandas / Scikit-learn  
- LightGCN  
- Jupyter / Redash  
- Pydantic, Uvicorn

---

## Endpoint: `/post/recommendations/`

### Method:
```
GET /post/recommendations/
```

### Parameters:
| Parameter | Type   | Description                                   |
|-----------|--------|-----------------------------------------------|
| `user_id` | `int`  | User ID                                      |
| `time`    | `str`  | Timestamp in ISO format                       |
| `limit`   | `int`  | Number of recommendations to return (default 5) |

Example:
```
GET /post/recommendations/?id=1234&time=2021-12-01T12:00:00&limit=5
```

### Example response:
```json
{
  "exp_group": "test",
  "recommendations": [
    {
      "id": 4087,
      "text": "How to deploy FastAPI with Uvicorn and Docker",
      "topic": "backend"
    },
    {
      "id": 1032,
      "text": "10 secrets of data preprocessing in ML",
      "topic": "machine_learning"
    },
    {
      "id": 2354,
      "text": "What is feature importance and how to use it",
      "topic": "data_science"
    }
  ]
}
```

If the user is not found, the top-5 liked posts are returned.

---

## Installation and running

### 1. Install dependencies
```bash
uv sync
```

### 2. Run API
```bash
uvicorn app.main:app --reload
```

The API will be available at:
[http://127.0.0.1:8000/post/recommendations](http://127.0.0.1:8000/post/recommendations)

---

## Author

Irina Nechetnaya

Project developed as part of ML and backend development learning and practice.  
Developed in the [StartML](https://karpov.courses/ml-start) program at karpov.courses
