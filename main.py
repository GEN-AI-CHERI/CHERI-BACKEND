from fastapi import FastAPI, Depends, Body, status, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

import scheme
import model
import crud
import database
import bcrypt
from util import jwt_util
from util import gpt_util

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*", "access-token", "access_token"],
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
    if crud.find_member_by_email(member=req, db=db):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "message": "Account(Email) already exists."
                            })
    member = crud.create_member(member=req, db=db)
    return {
        "message": "Sign Up Request Successes.",
        "email": str(member.email)
    }


@app.post("/members/signin")
async def member_sign_in(req: scheme.MemberSignInfo, db: Session = Depends(get_db)):
    member = crud.find_member_by_email(member=req, db=db)
    if not bcrypt.checkpw(req.password.encode('utf-8'), member.password.encode('utf-8')):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"message": "Your email or password is not valid."})
    access_token, refresh_token = jwt_util.create_jwt(member.member_id)
    return {
        "message": "Sign In Request Successes",
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@app.get("/members/me")
async def member_information(access_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    member_id = jwt_util.decode_jwt(access_token)['member_id']
    member = crud.find_member_by_pk(db=db, id=member_id)
    rooms = crud.find_chatrooms_by_member(db=db, id=member_id)
    return {
        "member": member,
        "room_list": rooms
    }


@app.get("/regions")
async def get_regions(db: Session = Depends(get_db)):
    region_list = crud.find_region_list(db=db)
    return {
        "regions": region_list
    }


@app.post("/chatrooms/start")
async def start_chat(req: scheme.ChatRoomInfo, access_token: str | None = Header(default=None),
                     db: Session = Depends(get_db)):
    themes = crud.find_themes(db=db, theme_list=req.theme)
    chatroom = crud.create_chatroom(db=db, req=req)
    chatroom_theme = crud.create_chatroom_theme(db=db, room_id=chatroom.room_id, themes=themes)
    member_id = jwt_util.decode_jwt(access_token)['member_id']
    room_member = crud.create_chat_member(db=db, member_id=member_id, room_id=chatroom.room_id)
    region = crud.find_region(db=db, id=chatroom.region_id)
    theme_str = ', '.join(t.keyword for t in themes)
    first_question = json.loads(
        gpt_util.get_completion(
            prompt="Recommand tour plan in " + region.title + ". I am " + chatroom.age + "years old. "
                   + "I want to travel from " + str(chatroom.begin_date) + "to " + str(chatroom.end_date) + ". Give "
                   + "Response only with json."
                   + "I like " + theme_str + " ."
                   + "Format is {"
                     "'plan':,"
                     "'description':,"
                     "itinerary: ["
                     "{'day':, 'description':, 'places':[],}"
                     "], recommend_next_questions:[]}. recommend_next_questions is your recommend for next question."
                     " the longer 'description' is the better. In 'description', describe about " + region.title + ", "
                   + "and give summary of tour plans. consider period of travel.")
    )
    chat = crud.create_chat(
        db=db,
        contents=first_question,
        isQuestion=False,
        room_id=chatroom.room_id
    )
    return {"room_id": chatroom.region_id,
            "chat_id": chat.chat_id,
            "member_id": member_id,
            "themes": theme_str.split(", "),
            "message": first_question
            }


@app.post("/chats")
async def tour_chat(req: scheme.ChatReq, db: Session = Depends(get_db)):
    print(req.prompt)
    answer = gpt_util.get_completion(prompt=req.prompt)
    print(answer)
    db_question, db_answer = crud.create_chat_question_answer(req, answer, db)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={
                            "room_id": req.room_id,
                            "question": {
                                "chat_id": db_question.chat_id,
                                "contents": db_question.contents
                            },
                            "answer": {
                                "chat_id": db_answer.chat_id,
                                "contents": db_answer.contents
                            }
                        })


@app.post("/chats/save")
async def request_chat(req: scheme.ChatRoomSaveReq,
                       access_token: str | None = Header(default=None),
                       db: Session = Depends(get_db)
                       ):
    member_id = jwt_util.decode_jwt(access_token)['member_id']
    room_member = crud.create_chat_member(db=db, member_id=member_id, room_id=req.room_id)
    return {"member_room_data": room_member}


@app.get("/chatrooms/{room_id}")
async def get_chatroom_chat(room_id: int, db: Session = Depends(get_db)):
    chat_list = crud.find_chats_by_room(db=db, room_id=room_id)
    return {
        "chats": chat_list
    }
