from sqlalchemy import Boolean, Column, ForeignKey, Date, DateTime, String, BigInteger
from sqlalchemy.orm import relationship

from database import Base


class Member(Base):
    __tablename__ = "member"

    member_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class Region(Base):
    __tablename__ = "region"

    region_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    title = Column(String, unique=True)
    description = Column(String)
    photo = Column(String)


class Activity(Base):
    __tablename__ = "activity"

    activity_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True)
    description = Column(String)
    photo = Column(String)
    region_id = Column(BigInteger, ForeignKey("region.region_id"))


class Room(Base):
    __tablename__ = "room"
    room_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    gender = Column(String)
    age = Column(String)
    begin_date = Column(Date)
    end_date = Column(Date)
    region_id = Column(BigInteger, ForeignKey("region.region_id"))
    region = relationship("Region", backref="region")


class Chat(Base):
    __tablename__ = "chat"
    chat_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    contents = Column(String)
    isQuestion = Column(Boolean)
    createdAt = Column(DateTime)
    room_id = Column(BigInteger, ForeignKey("room.room_id"))
    room = relationship("Room", backref="room")


class Theme(Base):
    __tablename__ = "theme"
    theme_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    keyword = Column(String)


class RoomTheme(Base):
    __tablename__ = "room_theme"
    room_theme_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("room.room_id"))
    theme_id = Column(BigInteger, ForeignKey("theme.theme_id"))


class MemberRoom(Base):
    __tablename__ = "member_room"
    member_room_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("room.room_id"))
    member_id = Column(BigInteger, ForeignKey("member.member_id"))
    member = relationship("Member", backref="owner")
    room = relationship("Room", backref="chat_room")
