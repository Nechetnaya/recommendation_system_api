"""
This module defines API endpoints related to users and their activity feed.

Endpoints:
- GET /user/{id}: Retrieve user data by user ID.
- GET /user/{id}/feed: Retrieve a list of recent feed actions by the specified user.

Dependencies:
- FastAPI for routing and dependency injection.
- SQLAlchemy ORM for database interaction.
- Schemas: `UserGet`, `FeedGet` for response models.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.table_feed import Feed
from app.db.table_user import User
from app.schema import UserGet, FeedGet

router = APIRouter(prefix="/user", tags=["users"])


@router.get("/{id}", response_model=UserGet)
def get_user(id:int, db: Session = Depends(get_db)):
    """Retrieve user data by user ID"""
    result = db.query(User).filter(User.id == id).first()
    if not result:
        raise HTTPException(404, "user is not found")
    else:
        return result


@router.get("/{id}/feed", response_model=List[FeedGet])
def get_feed_user(id:int, limit:int=10, db: Session = Depends(get_db)):
    """Retrieve a list of recent feed actions by the specified user"""
    result = (
        db.query(Feed)
        .filter(Feed.user_id == id)
        .order_by(Feed.time.desc())
        .limit(limit)
        .all()
    )
    return result
