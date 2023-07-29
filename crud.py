from sqlalchemy.orm import Session
from model import Member
import scheme
import bcrypt


def create_member(db: Session, member: scheme.SignUpInfo):
    db_member = Member(
        email=member.email,
        password=bcrypt.hashpw(member.password.encode('utf-8'), bcrypt.gensalt())
    )
    print(db_member.email)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member
