
# Recommendation Systems API

Content recommender system built with FastAPI and CatBoost, using user behavior, post text, and LightFM embeddings.  
Developed as a pet project to learn top-N recommendation modeling and API integration.

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
- User and post embeddings generated with LightFM  
- Text features extracted from posts (TFIDF + TruncatedSVD)  
- CatBoostClassifier trained and optimized for AUC  
- Integrated into FastAPI app with PostgreSQL connection  
- Supports recommendation queries filtering out already liked posts

### Results:
- HitRate@5 on test: **0.582**  
- AUC: **0.76**  
- API response time: < 500 ms for 5 recommendations

---

## Technology stack

- Python 3.8  
- FastAPI  
- CatBoost  
- SQLAlchemy + PostgreSQL  
- Pandas / Scikit-learn  
- LightFM  
- Jupyter / Redash  
- Pydantic, UV

---

## Project structure

```

.
├── app/                    # FastAPI application
│   ├── api/                # Routes and request handlers
│   ├── core/               # Model and data loading
│   ├── db/                 # SQLAlchemy models and sessions
│   ├── schema.py           # Pydantic schemas
│   └── main.py             # FastAPI entrypoint
│
├── recommender/            # Model training
│   ├── notebooks/          # Jupyter research notebooks
│   └──train\_data/         # Sample train/feature data         
│
├── models/                 # Saved CatBoost models
├── pyproject.toml
├── Makefile
└── README.md

```

---

## Data Examples (`recommender/train_data/`)

Contains examples:

- `train_sample.csv` — ~2K rows training subset

- `user_features.csv` — user_id + features:
  - `age_group` — categorical  
  - `country` — categorical  
  - `exp_group` — encrypted experimental group  
  - `views_day` — average number of views per day  
  - `movie_views_rate` — share of views for the "movie" topic from all views  
  - `movie_likes_rate`, `covid_likes_rate`, `sport_likes_rate`, `politics_likes_rate`, `business_likes_rate`, `tech_likes_rate` — conversion rates from views to likes by post topic  
  - `user_emb_0` … `user_emb_9` — LightFM user embeddings

- `post_features.csv` — post_id + features:
  - `topic` — post topic  
  - `likes_rating` — rank by total likes  
  - `tfidf_0` … `tfidf_9` — post text embeddings (TFIDF + SVD)  
  - `post_emb_0` … `post_emb_9` — LightFM post embeddings

- `likes.csv` — `timestamp`, `user_id`, `post_id` (used to exclude already liked posts)

---

## Endpoint: `/post/recommendations/`

### Method:
```

GET /post/recommendations/

```

### Parameters:
| Parameter | Type   | Description                                   |
|-----------|--------|-----------------------------------------------|
| `id`      | `int`  | User ID                                      |
| `time`    | `str`  | Timestamp in ISO format                       |
| `limit`   | `int`  | Number of recommendations to return (default 5) |

Example:
```

GET /post/recommendations/?id=1234\&time=2021-12-01T12:00:00\&limit=5

````

### Example response:
```json
[
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
````

If the user is not found, an empty list `[]` is returned.

---

## Installation and running

### 1. Install dependencies

```bash
uv install
```

### 2. Run API

```bash
uvicorn app.main:app --reload
```

The API will be available at:
[http://127.0.0.1:8000/post/recommendations](http://127.0.0.1:8000/post/recommendations)

---

##  TODO

* [ ] Add unit tests
* [ ] Add Dockerfile and docker-compose

---

## Author

Irina Nechetnaya

Project developed as part of ML and backend development learning and practice.
Developed in the [StartML](https://karpov.courses/ml-start) program at karpov.courses
