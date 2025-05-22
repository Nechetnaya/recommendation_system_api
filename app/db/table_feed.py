from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.database import Base

from app.db.table_user import User
from app.db.table_post import Post

# orm for table "feed_action"
class Feed(Base):
    __tablename__ = "feed_action"

    user_id = Column(Integer, ForeignKey(User.__table__.c.id), primary_key=True)
    user = relationship("User")
    post_id = Column(Integer, ForeignKey(Post.__table__.c.id), primary_key=True)
    post = relationship("Post")
    action = Column(String)
    time = Column(TIMESTAMP)
