from fastapi import FastAPI
import scheme
import crud
from sqlalchemy.orm import Session

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/signup")
async def member_sign_up(req: scheme.SignUpInfo):
    member = crud.create_member(member=req)
    return {
        "message": "Sign Up Request Successed.",
        "email": str(member.email)
    }
