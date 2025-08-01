"""
ORM model for the 'user' table representing user profiles.

Attributes:
- id (int, PK): Unique user identifier.
- gender (int): User gender code.
- age (int): User age.
- country (str): User country.
- city (str): User city.
- exp_group (int): Experiment group assignment.
- os (str): User device operating system.
- source (str): User acquisition source.

Includes a test query that counts users by country and OS in experiment group 3,
filtering groups with more than 100 users, ordered by count descending.
"""

from sqlalchemy import Column, Integer, String, func
from app.db.database import Base, SessionLocal


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

# Test query: count users grouped by country and OS in experiment group 3
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
