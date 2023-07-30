import datetime

import jwt
import os
from dotenv import load_dotenv


def create_jwt(member_id: int):
    return get_jwt_secret(member_id)


def get_jwt_secret(member_id: int):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(BASE_DIR, "../.env"))
    SECRET = os.environ.get("JWT_SECRET")
    access_token = jwt.encode(
        {
            "member_id":member_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=172800)
        },
        SECRET,
        algorithm="HS256"
    )
    refresh_token = jwt.encode(
        {
            "member_id": member_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=400000)
        },
        SECRET,
        algorithm="HS256"
    )
    return access_token, refresh_token
