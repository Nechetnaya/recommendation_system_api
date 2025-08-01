"""
Main entry point for the StartML Recommendation System API.

- Initializes FastAPI application.
- Loads models and feature data on startup.
- Includes routers for user, post, and recommendation endpoints.

Routes:
- GET /: Health check root endpoint returning project info.
"""

import uvicorn
from fastapi import FastAPI
from app.core import state
from app.core.model_loader import load_models
from app.core.features_loader import load_features, select_top_liked_posts_ids
from app.api import users, posts, recommend

app = FastAPI(title="StartML Recommendation System")


@app.on_event("startup")
def startup_event():
    """
    Load models and feature data into global state on application startup.
    """
    print("Loading model and features on startup...")
    state.model_test, state.model_control = load_models()
    state.users_data = load_features('users')
    state.posts_data = load_features('posts')
    state.top_5_posts_list = select_top_liked_posts_ids(5)
    print("Model and features loaded.")

# Register API routes
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(recommend.router)

@app.get("/")
def read_root():
    return {"message": "StartML course Project: Recommendations"}

if __name__ == "__main__":
    # Run the FastAPI app with live reload for development
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
