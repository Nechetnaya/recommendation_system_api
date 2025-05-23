from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import state
from app.db.database import get_db
from app.db.table_post import Post
from app.schema import PostGet
from app.core.recommender import get_recommend_ids

router = APIRouter(prefix="/post", tags=["recommendations"])


@router.get("/recommendations/", response_model=List[PostGet])
def recommended_posts(
        user_id: int,
        time: datetime,
        limit: int = 5,
        db: Session = Depends(get_db)
) -> List[PostGet]:
    """Recommended posts for user {id}"""
    post_ids = get_recommend_ids(user_id, time, limit=limit)
    if not post_ids:
        post_ids = state.top_5_posts_list

    posts = db.query(Post).filter(Post.id.in_(post_ids)).all()

    post_dict = {post.id: post for post in posts}
    ordered_posts = [post_dict[pid] for pid in post_ids if pid in post_dict]

    return ordered_posts

