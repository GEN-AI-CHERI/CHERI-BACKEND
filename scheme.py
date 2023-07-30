from pydantic import BaseModel


class MemberSignInfo(BaseModel):
    email: str
    password: str
