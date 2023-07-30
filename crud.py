from sqlalchemy.orm import Session
from model import Member
import scheme
import bcrypt


def create_member(db: Session, member: scheme.MemberSignInfo):
    haswed_password = bcrypt.hashpw(member.password.encode('utf-8'), bcrypt.gensalt())
    db_member = Member(
        email=member.email,
        password=haswed_password.decode('utf-8')
    )
    print(db_member.email)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def find_member_by_email(db: Session, member: scheme.MemberSignInfo):
    db_member = db.query(Member).filter(
        member.email == Member.email
    )
    if db_member:
        for m in db_member:
            return m
    else:
        return None