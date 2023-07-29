from pydantic import BaseModel


class SignUpInfo(BaseModel):
    email: str
    password: str
