import uvicorn
from fastapi import FastAPI
from app.core import state
from app.core.model_loader import load_models
from app.core.features_loader import load_features, select_top_liked_posts_ids
from app.api import users, posts, recommend

app = FastAPI(title="StartML Recommendation System")


@app.on_event("startup")
def startup_event():
    print("Loading model and features on startup...")
    state.model_test, state.model_control = load_models()
    state.users_data = load_features('users')
    state.posts_data = load_features('posts')
    state.top_5_posts_list = select_top_liked_posts_ids(5)
    print("Model and features loaded.")

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(recommend.router)

@app.get("/")
def read_root():
    return {"message": "StartML course Project: Recommendations"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
