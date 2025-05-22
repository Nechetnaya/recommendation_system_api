from sqlalchemy import Column, Integer, String, func
from src.database import Base, SessionLocal

# orm for table "user"
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    gender = Column(Integer)
    age = Column(Integer)
    country = Column(String)
    city = Column(String)
    exp_group = Column(Integer)
    os = Column(String)
    source = Column(String)

# check
if __name__ == "__main__":
    with SessionLocal() as session:
        result = (
            session.query(User.country,
                          User.os,
                          func.count(User.id).label('user_count'))
            .filter(User.exp_group == 3)
            .group_by(User.country, User.os)
            .having(func.count(User.id) > 100)
            .order_by(func.count(User.id).desc())
            .all()
        )
    result = ([(user.country, user.os, user.user_count) for user in result])
    print(result)
