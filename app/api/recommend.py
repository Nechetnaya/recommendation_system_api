import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import state
from app.db.database import get_db
from app.db.table_post import Post
from app.schema import Response
from app.core.recommender import get_recommend_ids
from app.core.ab_groups import get_exp_group

router = APIRouter(prefix="/post", tags=["recommendations"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/recommendations/", response_model=Response)
def recommended_posts(
        user_id: int,
        time: datetime,
        limit: int = 5,
        db: Session = Depends(get_db)
) -> Response:
    """Recommended posts for user {id}"""
    exp_group = get_exp_group(user_id)

    if exp_group == 'test':
        post_ids = get_recommend_ids(user_id, time, state.model_test, limit)
        logger.info(f"user_id={user_id} | exp_group=test | model=model_test | posts={post_ids}")
    elif exp_group == 'control':
        post_ids = get_recommend_ids(user_id, time, state.model_control, limit)
        logger.info(f"user_id={user_id} | exp_group=control | model=model_control | posts={post_ids}")
    else:
        raise ValueError('unknown group')

    if not post_ids:
        post_ids = state.top_5_posts_list

    posts = db.query(Post).filter(Post.id.in_(post_ids)).all()

    post_dict = {post.id: post for post in posts}
    ordered_posts = [post_dict[pid] for pid in post_ids if pid in post_dict]

    return Response(exp_group=exp_group, recommendations=ordered_posts)


