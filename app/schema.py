"""
Pydantic models for request/response validation and ORM serialization.

Models:
- UserGet: Schema for returning user data.
- PostGet: Schema for returning post data.
- Response: Schema for recommendation response with experiment group info.
- FeedGet: Schema for user-post interaction data (feed actions).
"""

import datetime
from typing import List

from pydantic import BaseModel

# users data validation
class UserGet(BaseModel):
    id: int
    gender: int
    age: int
    country: str
    city: str
    exp_group: int
    os: str
    source: str

    class Config:
        orm_mode = True

class PostGet(BaseModel):
    id: int
    text: str
    topic: str

    class Config:
        orm_mode = True


class Response(BaseModel):
    exp_group: str
    recommendations: List[PostGet]

# actions data validation
class FeedGet(BaseModel):
    user_id: int
    user: UserGet
    post_id: int
    post: PostGet
    action: str
    time: datetime.datetime

    class Config:
        orm_mode = True
