"""
ORM model for the 'post' table representing posts content.

Attributes:
- id (int, PK): Unique identifier of the post.
- text (str): Text content of the post.
- topic (str): Topic/category of the post.

Includes a test query to fetch the 10 most recent posts with topic 'business'.
"""

from sqlalchemy import Column, Integer, String
from app.db.database import Base, SessionLocal


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)

# Test querying the latest 10 posts in the "business" topic
if __name__ == "__main__":
    with SessionLocal() as session:
        result = (
            session.query(Post)
            .filter(Post.topic == "business")
            .order_by(Post.id.desc())
            .limit(10)
            .all()
        )
    print([post.id for post in result])
