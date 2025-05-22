from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.popular import fetch_top_liked_posts
from app.db.database import get_db
from app.db.table_post import Post
from app.schema import PostGet
from app.core.recommender import get_recommend_ids

router = APIRouter(prefix="/post", tags=["recommendations"])


@router.get("/recommendations/", response_model=List[PostGet])
def recommended_posts(
        id: int,
        time: datetime,
        limit: int = 5,
        db: Session = Depends(get_db)
) -> List[PostGet]:
    """Recommended posts for user {id}"""
    post_ids = get_recommend_ids(id, time, limit=limit)
    if not post_ids:
        return fetch_top_liked_posts(limit, db)

    posts = db.query(Post).filter(Post.id.in_(post_ids)).all()

    post_dict = {post.id: post for post in posts}
    ordered_posts = [post_dict[pid] for pid in post_ids if pid in post_dict]

    return ordered_posts

