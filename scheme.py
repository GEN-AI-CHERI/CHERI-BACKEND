from pydantic import BaseModel
from datetime import datetime


class MemberSignInfo(BaseModel):
    email: str
    password: str


class ChatRoomInfo(BaseModel):
    gender: str
    age: str
    begin_date: str
    end_date: str
    region_id: int
