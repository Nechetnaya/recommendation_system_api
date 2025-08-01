"""
API endpoints for retrieving posts and related feed actions.

This module defines routes under the "/post" prefix for accessing individual posts,
their associated feed actions, and a list of top liked posts.

Endpoints:
- GET /post/{id}: Retrieve a post by its ID.
- GET /post/{id}/feed: Retrieve feed actions related to a specific post.
- GET /post/top-liked: Retrieve the top liked posts.

Dependencies:
- SQLAlchemy Session from `get_db`
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.features_loader import select_top_liked_posts_ids
from app.db.database import get_db
from app.db.table_post import Post
from app.db.table_feed import Feed
from app.schema import PostGet, FeedGet

router = APIRouter(prefix="/post", tags=["posts"])


@router.get("/{id}", response_model=PostGet)
def get_post(id:int, db: Session = Depends(get_db)):
    """ Retrieve a post by its ID."""
    result = db.query(Post).filter(Post.id == id).first()
    if not result:
        raise HTTPException(404, "post is not found")
    else:
        return result


@router.get("/{id}/feed", response_model=List[FeedGet])
def get_feed_post(id:int, limit:int=10, db: Session = Depends(get_db)):
    """Retrieve feed actions related to a specific post."""
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
    """Retrieve the top liked posts."""
    top_posts = select_top_liked_posts_ids(limit)
    posts = db.query(Post).filter(Post.id.in_(top_posts)).all()

    post_dict = {post.id: post for post in posts}
    ordered_posts = [post_dict[pid] for pid in top_posts if pid in post_dict]

    return ordered_posts
