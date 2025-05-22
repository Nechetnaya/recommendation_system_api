import uvicorn
from fastapi import FastAPI
from app.core import state
from app.core.model_loader import load_models
from app.core.features_loader import load_features
from app.api import users, posts, recommend

app = FastAPI(title="StartML Recommendation System")


@app.on_event("startup")
def startup_event():
    global model, users_data, posts_data
    print("Loading model and features on startup...")
    state.model = load_models()
    state.users_data = load_features('users')
    state.posts_data = load_features('posts')
    print("Model and features loaded.")

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(recommend.router)

@app.get("/")
def read_root():
    return {"message": "StartML course Project: Recommendations"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
