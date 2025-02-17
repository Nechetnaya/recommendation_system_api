import uvicorn
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from table_user import User
from table_post import Post
from table_feed import Feed
from schema import UserGet, PostGet, FeedGet

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
