"""
ORM model for 'feed_action' table representing user interactions with posts.

Columns:
- user_id (int, PK, FK): ID of the user performing the action.
- post_id (int, PK, FK): ID of the post on which action was performed.
- action (str): Type of action (e.g., like, view).
- time (TIMESTAMP): Timestamp of the action.

Relationships:
- user: SQLAlchemy relationship to User model.
- post: SQLAlchemy relationship to Post model.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.database import Base

from app.db.table_user import User
from app.db.table_post import Post


class Feed(Base):
    __tablename__ = "feed_action"

    user_id = Column(Integer, ForeignKey(User.__table__.c.id), primary_key=True)
    user = relationship("User")
    post_id = Column(Integer, ForeignKey(Post.__table__.c.id), primary_key=True)
    post = relationship("Post")
    action = Column(String)
    time = Column(TIMESTAMP)
