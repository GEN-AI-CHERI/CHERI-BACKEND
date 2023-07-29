from sqlalchemy.orm import Session
import model
import scheme
import bcrypt


def create_member(member: scheme.SignUpInfo):
    print(member.email)
    print(bcrypt.hashpw(member.password.encode('utf-8'), bcrypt.gensalt()))
    db_member = model.Member(email=member.email,
                             password=bcrypt.hashpw(member.password.encode('utf-8'), bcrypt.gensalt()))
    Session.add(db_member)
    Session.commit()
    Session.refresh(db_member)
    return db_member
