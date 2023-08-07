import datetime

from sqlalchemy.orm import Session, joinedload
from model import Member
from model import Region, Scrap
from model import Room, MemberRoom, Chat
from model import Theme, RoomTheme
from model import Recommend
from model import Guide, GuideImage
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
    db_regions = db.query(Region).all()
    return db_regions


def find_chats_by_room(db: Session, room_id: int):
    chats = db.query(Chat).filter(Chat.room_id == room_id)
    chat_list = []
    for c in chats:
        chat_list.append(c)
    return chat_list


def create_chatroom(db: Session, req: scheme.ChatRoomInfo):
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
    return db_chatroom


def find_region(db: Session, id: int):
    db_region = db.query(Region).get(id)
    return db_region


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
        contents=req.prompt,
        createdAt=datetime.datetime.now()
    )
    db_answer = Chat(
        room_id=req.room_id,
        isQuestion=False,
        contents=chat,
        createdAt=datetime.datetime.now()
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
    db.add(db_member_room)
    db.commit()
    db.refresh(db_member_room)
    return db_member_room


def find_member_by_pk(db: Session, id: int):
    return db.query(Member).get(id)


def find_chatrooms_by_member(db: Session, id: int):
    rooms = db.query(Room).options(joinedload(Room.region)) \
        .join(MemberRoom.room).filter(MemberRoom.member_id == id).all()
    room_list = []
    for r in rooms:
        t = find_chatroom_theme(db=db, room_id=r.room_id)
        theme_list = []
        for i in t:
            theme_list.append(i.theme.keyword)
        r.themes = theme_list
        if isinstance(r.begin_date, datetime.date):
            r.begin_date.strftime('%Y-%m-%d')
            r.end_date.strftime('%Y-%m-%d')
        room_list.append(r)
    return room_list


def find_themes(db: Session, theme_list: list):
    all_theme = db.query(Theme).all()
    themes = []
    for t in all_theme:
        if t.theme_id in theme_list:
            themes.append(t)
    return themes


def create_chatroom_theme(db: Session, room_id: int, themes: int):
    db_room_theme = []
    for t in themes:
        db_room_theme.append(RoomTheme(theme_id=t.theme_id, room_id=room_id))
    db.add_all(db_room_theme)
    db.commit()
    for d in db_room_theme:
        db.refresh(d)
    return None


def find_chatroom_theme(db: Session, room_id: int):
    return db.query(RoomTheme).options(joinedload(RoomTheme.room)).filter(RoomTheme.room_id == room_id)


def create_scrap(db: Session, member_id: int, region_id: int):
    db_scrap = Scrap(member_id=member_id, region_id=region_id)
    db.add(db_scrap)
    db.commit()
    db.refresh(db_scrap)
    return db_scrap


def find_scrap_by_member_pk(db, member_id: int):
    scrap = db.query(Scrap).options(joinedload(Scrap.region)).filter(Scrap.member_id == member_id).all()
    return scrap


def create_recommend(db, member_id: int, region_id: int):
    db_recommend = Recommend(member_id=member_id, region_id=region_id)
    print(db_recommend.region_id)
    db.add(db_recommend)
    db.commit()
    db.refresh(db_recommend)
    return db_recommend


def find_recommend_by_member_pk(db, member_id: int):
    recommend = db.query(Recommend).options(joinedload(Recommend.region)).filter(Recommend.member_id == member_id).all()
    return recommend


def find_guides(db: Session):
    return db.query(Guide).options(joinedload(Guide.region)).all()


def find_guide(db: Session, guide_id: int):
    return db.query(Guide).get(guide_id)


def find_guides_by_region(db: Session, region_id: int):
    return db.query(Guide).options(joinedload(Guide.region)).filter(Guide.region_id == region_id).all()


def find_guides_info(db: Session, guide_id: int):
    return db.query(GuideImage).options(joinedload(GuideImage.guide)).filter(GuideImage.guide_id == guide_id).all()


def find_recommend_by_pk(db: Session, recommend_id: int):
    return db.query(Recommend).options(joinedload(Recommend.region)).get(recommend_id)


def find_scrap_by_member_and_region(db, member_id: int, region_id: int):
    scrap = db.query(Scrap).options(joinedload(Scrap.region)).filter(Scrap.member_id == member_id, Scrap.region_id == region_id)
    if len(list(scrap)) > 0:
        return scrap[0]
