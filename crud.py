import datetime

from sqlalchemy.orm import Session
from model import Member
from model import Region
from model import Room
from model import Chat
from model import MemberRoom
import scheme
import bcrypt


def create_member(db: Session, member: scheme.MemberSignInfo):
    hashed_password = bcrypt.hashpw(member.password.encode('utf-8'), bcrypt.gensalt())
    db_member = Member(
        email=member.email,
        password=hashed_password.decode('utf-8')
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def find_member_by_email(db: Session, member: scheme.MemberSignInfo):
    db_member = db.query(Member).filter(member.email == Member.email)
    if db_member:
        for m in db_member:
            return m


def find_region_list(db: Session):
    return db.query(Region).all()


def create_chatroom(db: Session, req: scheme.ChatRoomInfo):
    print(req.region_id)
    db_chatroom = Room(
        gender=req.gender,
        age=req.age,
        begin_date=req.begin_date,
        end_date=req.end_date,
        region_id=req.region_id
    )
    db.add(db_chatroom)
    db.commit()
    db.refresh(db_chatroom)
    print(db_chatroom)
    return db_chatroom


def find_region(db: Session, id: int):
    return db.query(Region).get(id)


def create_chat(db: Session, contents, isQuestion, room_id):
    db_chat = Chat(
        room_id=room_id,
        isQuestion=isQuestion,
        contents=str(contents),
        createdAt=datetime.datetime.now()
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def create_chat_question_answer(req: scheme.ChatReq, chat, db: Session):
    db_question = Chat(
        room_id=req.room_id,
        isQuestion=True,
        contents=req.prompt
    )
    db_answer = Chat(
        room_id=req.room_id,
        isQuestion=False,
        contents=chat
    )
    db.add_all([db_question, db_answer])
    db.commit()
    db.refresh(db_question)
    db.refresh(db_answer)
    return db_question, db_answer


def create_chat_member(db: Session, room_id: int, member_id: int):
    db_member_room = MemberRoom(
        room_id=room_id,
        member_id=member_id
    )
    db.add_all(db_member_room)
    db.commit()
    db.refresh(db_member_room)
    return db_member_room
