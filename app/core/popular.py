from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.table_post import Post
from app.db.table_feed import Feed


def fetch_top_liked_posts(limit: int, db: Session) -> List[Post]:
    return (
        db.query(Post)
        .join(Feed, Post.id == Feed.post_id)
        .filter(Feed.action == 'like')
        .group_by(Post.id)
        .order_by(func.count(Feed.post_id).desc())
        .limit(limit)
        .all()
    )
