from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.popular import fetch_top_liked_posts
from app.db.database import get_db
from app.db.table_post import Post
from app.db.table_feed import Feed
from app.schema import PostGet, FeedGet

router = APIRouter(prefix="/post", tags=["posts"])


@router.get("/{id}", response_model=PostGet)
def get_post(id:int, db: Session = Depends(get_db)):
    """get post by id"""
    result = db.query(Post).filter(Post.id == id).first()
    if not result:
        raise HTTPException(404, "post is not found")
    else:
        return result


@router.get("/{id}/feed", response_model=List[FeedGet])
def get_feed_post(id:int, limit:int=10, db: Session = Depends(get_db)):
    """get all actions related to post by id"""
    result = (
        db.query(Feed)
        .filter(Feed.post_id == id)
        .order_by(Feed.time.desc())
        .limit(limit)
        .all()
    )
    return result


@router.get("/top-liked", response_model=List[PostGet])
def get_top_liked_posts(limit: int = 10, db: Session = Depends(get_db)):
    return fetch_top_liked_posts(limit, db)
