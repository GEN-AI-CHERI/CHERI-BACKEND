from pydantic import BaseModel
from datetime import datetime


class MemberSignInfo(BaseModel):
    email: str
    password: str


class ChatRoomInfo(BaseModel):
    gender: str
    age: str
    theme: list
    begin_date: str
    end_date: str
    region_id: int


class ChatReq(BaseModel):
    prompt: str
    room_id: int


class ChatRoomSaveReq(BaseModel):
    room_id: int
