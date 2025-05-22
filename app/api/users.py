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
    """get user by id"""
    result = db.query(User).filter(User.id == id).first()
    if not result:
        raise HTTPException(404, "user is not found")
    else:
        return result


@router.get("/{id}/feed", response_model=List[FeedGet])
def get_feed_user(id:int, limit:int=10, db: Session = Depends(get_db)):
    """get all actions of user by id"""
    result = (
        db.query(Feed)
        .filter(Feed.user_id == id)
        .order_by(Feed.time.desc())
        .limit(limit)
        .all()
    )
    return result
