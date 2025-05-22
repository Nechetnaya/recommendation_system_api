from sqlalchemy import Column, Integer, String
from app.db.database import Base, SessionLocal

# orm for table "post"
class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)

# check
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
