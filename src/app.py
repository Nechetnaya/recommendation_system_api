import uvicorn
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database import SessionLocal
from src.table_user import User
from src.table_post import Post
from src.table_feed import Feed
from src.schema import UserGet, PostGet, FeedGet

app = FastAPI()


# connection to startml
def get_db():
    with SessionLocal() as db:
        return db


@app.get("/user/{id}", response_model=UserGet)
def get_user(id:int, db: Session = Depends(get_db)):
    """get user by id"""
    result = db.query(User).filter(User.id == id).first()
    if not result:
        raise HTTPException(404, "user is not found")
    else:
        return result


@app.get("/post/{id}", response_model=PostGet)
def get_post(id:int, db: Session = Depends(get_db)):
    """get post by id"""
    result = db.query(Post).filter(Post.id == id).first()
    if not result:
        raise HTTPException(404, "post is not found")
    else:
        return result


@app.get("/user/{id}/feed", response_model=List[FeedGet])
def get_feed(id:int, limit:int=10, db: Session = Depends(get_db)):
    """get all actions of user by id"""
    result = (
        db.query(Feed)
        .filter(Feed.user_id == id)
        .order_by(Feed.time.desc())
        .limit(limit)
        .all()
    )
    return result


@app.get("/post/{id}/feed", response_model=List[FeedGet])
def get_feed(id:int, limit:int=10, db: Session = Depends(get_db)):
    """get all actions related to post by id"""
    result = (
        db.query(Feed)
        .filter(Feed.post_id == id)
        .order_by(Feed.time.desc())
        .limit(limit)
        .all()
    )
    return result


@app.get("/post/recommendations/", response_model=List[PostGet])
def get_feed(limit:int=10, db: Session = Depends(get_db)):
    """get top-{limit} most liked posts"""
    result = (
        db.query(Post)
        .join(Feed, Post.id == Feed.post_id)
        .filter(Feed.action == 'like')
        .group_by(Post.id)
        .order_by(func.count(Feed.post_id).desc())
        .limit(limit)
        .all()
    )
    return result


if __name__ == '__main__':
    uvicorn.run(app)
