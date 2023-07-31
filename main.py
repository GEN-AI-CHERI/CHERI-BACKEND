from fastapi import FastAPI, Depends, Body, status, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

import scheme
import crud
import database
import bcrypt
from util import jwt_util
from util import gpt_util

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/members/signup")
async def member_sign_up(req: scheme.MemberSignInfo, db: Session = Depends(get_db)):
    member = crud.create_member(member=req, db=db)
    return {
        "message": "Sign Up Request Successes.",
        "email": str(member.email)
    }


@app.post("/members/signin")
async def member_sign_in(req: scheme.MemberSignInfo, db: Session = Depends(get_db)):
    member = crud.find_member_by_email(member=req, db=db)
    if not bcrypt.checkpw(req.password.encode('utf-8'), member.password.encode('utf-8')):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"Your email or password is not valid."})
    access_token, refresh_token = jwt_util.create_jwt(member.member_id)
    return {
        "message": "Sign In Request Successes",
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@app.get("/regions")
async def get_regions(db: Session = Depends(get_db)):
    region_list = crud.find_region_list(db = db)
    return {
        "regions":region_list
    }


@app.post("/chat")
async def tour_chat():
    return json.loads(
        gpt_util.get_completion(prompt="Recommand tour plan in Seoul, Korea, for 3 days. Give Response only with json")
    )
