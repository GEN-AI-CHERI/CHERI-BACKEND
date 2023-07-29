from sqlalchemy import Boolean, Column, ForeignKey, Date, DateTime, String, BigInteger
from sqlalchemy.orm import relationship

from database import Base


class Member(Base):
    __tablename__ = "member"

    member_id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class Region(Base):
    __tablename__ = "region"

    region_id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    photo = Column(String)


class Activity(Base):
    __tablename__ = "activity"

    activity_id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    photo = Column(String)
    region_id = Column(BigInteger, ForeignKey("region.region_id"))
    region = relationship("Region", back_populates="region")


class Room(Base):
    __tablename__ = "room"
    room_id = Column(BigInteger, primary_key=True, index=True)
    gender = Column(String)
    age = Column(String)
    begin_date = Column(Date)
    end_date = Column(Date)
    region_id = Column(BigInteger, ForeignKey("region.region_id"))
    region = relationship("Region", back_populates="region")


class Chat(Base):
    __tablename__ = "chat"
    chat_id = Column(BigInteger, primary_key=True, index=True)
    contents = Column(String)
    isQuestion = Column(Boolean)
    createdAt = Column(DateTime, default="current")
    room_id = Column(BigInteger, ForeignKey("room.room_id"))
    room = relationship("Room", back_populates="room")


class Theme(Base):
    __tablename__ = "theme"
    theme_id = Column(BigInteger, primary_key=True, index=True)
    keyword = Column(String)


class RoomTheme(Base):
    __tablename__ = "room_theme"
    room_theme_id = Column(BigInteger, primary_key=True, index=True)
    room_id = Column(BigInteger, ForeignKey("room.room_id"))
    theme_id = Column(BigInteger, ForeignKey("theme.theme_id"))
    room = relationship("Room", back_populates="room")
    theme = relationship("Theme", back_populates="theme")


class MemberRoom(Base):
    __tablename__ = "member_room"
    member_room_id = Column(BigInteger, primary_key=True, index=True)
    room_id = Column(BigInteger, ForeignKey("room.room_id"))
    member_id = Column(BigInteger, ForeignKey("member.member_id"))
    room = relationship("Room", back_populates="room")
    member = relationship("Member", back_populates="member")
