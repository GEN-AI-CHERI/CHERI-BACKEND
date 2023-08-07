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
    allow_origins=["*", "https://cheri-front.vercel.app/", "http://localhost:3000", "https://cheritalk.site/"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*", "access-token", "access_token", "Authorization"],
    allow_credentials=False
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


@app.post("/scrap")
async def member_region_scrap(req: scheme.ScrapInfo, Authorization: str | None = Header(default=None),
                              db: Session = Depends(get_db)):
    member_id = jwt_util.decode_jwt(Authorization)['member_id']
    db_scrap = crud.create_scrap(db=db, member_id=member_id, region_id=req.region_id)
    return {
        "message": "Scrap Successes",
        "info": db_scrap
    }


@app.get("/members/me")
async def member_information(Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    member_id = jwt_util.decode_jwt(Authorization)['member_id']
    member = crud.find_member_by_pk(db=db, id=member_id)
    rooms = crud.find_chatrooms_by_member(db=db, id=member_id)
    scraps = crud.find_scrap_by_member_pk(db=db, member_id=member_id)
    recommends = crud.find_recommend_by_member_pk(db=db, member_id=member_id)
    return {
        "member": member,
        "room_list": rooms,
        "scrap_list": scraps,
        "recommends_list": recommends
    }


@app.get("/guides")
async def get_guides(db: Session = Depends(get_db)):
    guides = crud.find_guides(db=db)
    return {
        "guides": guides
    }


@app.get("/guides/region/{region_id}")
async def get_guides_by_region(region_id: int, db: Session = Depends(get_db)):
    guides = crud.find_guides_by_region(db=db, region_id=region_id)
    return {
        "guides": guides
    }


@app.get("/guides/{guide_id}")
async def get_guide_specific(guide_id: int, db: Session = Depends(get_db)):
    guide = crud.find_guide(db=db, guide_id=guide_id)
    guide_info = crud.find_guides_info(db=db, guide_id=guide_id)
    return {
        "guide": guide,
        "guide_info": guide_info
    }


@app.get("/regions")
async def get_regions(db: Session = Depends(get_db), Authorization: str | None = Header(default=None)):
    region_list = crud.find_region_list(db=db)
    for r in region_list:
        if r.detail:
            r.detail = r.detail.split("\n\n")
    if Authorization:
        member_id = jwt_util.decode_jwt(Authorization)['member_id']
        scraps = crud.find_scrap_by_member_pk(db=db, member_id=member_id)
        scrap_check = []
        for s in scraps:
            scrap_check.append(s.region_id)
        for r in region_list:
            if r.region_id in scrap_check:
                r.scrap = True
            else:
                r.scrap = False
    return {
        "regions": region_list
    }


@app.get("/regions/{region_id}")
async def get_region(region_id: int, db: Session = Depends(get_db)):
    region = crud.find_region(db=db, id=region_id)
    region.detail = region.detail.split("\n\n")
    return region


@app.post("/chatrooms/start")
async def start_chat(req: scheme.ChatRoomInfo, Authorization: str | None = Header(default=None),
                     db: Session = Depends(get_db)):
    themes = crud.find_themes(db=db, theme_list=req.theme)
    chatroom = crud.create_chatroom(db=db, req=req)
    chatroom_theme = crud.create_chatroom_theme(db=db, room_id=chatroom.room_id, themes=themes)
    member_id = jwt_util.decode_jwt(Authorization)['member_id']
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
    guide_list = crud.find_guides_by_region(db=db, region_id=region.region_id)
    return {"room_id": chatroom.room_id,
            "chat_id": chat.chat_id,
            "member_id": member_id,
            "themes": theme_str.split(", "),
            "message": first_question,
            "guide": guide_list
            }


@app.post("/chats")
async def tour_chat(req: scheme.ChatReq, db: Session = Depends(get_db)):
    answer = gpt_util.get_completion(prompt=req.prompt)
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
                                "contents": db_answer.contents.split("\n\n")
                            }
                        })


@app.post("/recommend")
async def tour_chat(req: scheme.RecommendReq, Authorization: str | None = Header(default=None),
                    db: Session = Depends(get_db)):
    themes = crud.find_themes(db=db, theme_list=req.theme)
    theme_str = ', '.join(t.keyword for t in themes)
    region_list = crud.find_region_list(db=db)
    region_str = ','.join(str(r.region_id) + " " + r.title + " " for r in region_list)
    member_id = jwt_util.decode_jwt(Authorization)['member_id']
    recommend = gpt_util.get_completion(
        prompt="I want to travel korea, within below cities \n"
               + region_str + "\n give response only with city's number. Only one city and only one number. don't "
                              "describe"
                              "about it. give response 'only' number. dont give me text."
               + "I will travel with " + req.with_who
               + ". I am " + req.age + "years old. "
               + "I want to travel from " + str(req.begin_date) + "to " + str(req.end_date)
               + "I like " + theme_str + " ."
    )
    region = crud.find_region(db=db, id=int(recommend))
    db_recommend = crud.create_recommend(db=db, member_id=member_id, region_id=region.region_id)
    db_recommend.region.detail = db_recommend.region.detail.split("\n\n")
    return {
        "recommend_id": db_recommend.recommend_id,
        "begin_date": req.begin_date,
        "end_date": req.end_date,
        "region": db_recommend.region,
        "themes": theme_str.split(', '),
    }


@app.get("/recommend/{recommend_id}")
async def get_recommend(recommend_id: int, db: Session = Depends(get_db)):
    recommend = crud.find_recommend_by_pk(db, recommend_id)
    recommend.region.detail = recommend.region.detail.split("\n\n")
    return recommend


@app.post("/chats/save")
async def request_chat(req: scheme.ChatRoomSaveReq,
                       Authorization: str | None = Header(default=None),
                       db: Session = Depends(get_db)
                       ):
    member_id = jwt_util.decode_jwt(Authorization)['member_id']
    room_member = crud.create_chat_member(db=db, member_id=member_id, room_id=req.room_id)
    return {"member_room_data": room_member}


@app.get("/chatrooms/{room_id}")
async def get_chatroom_chat(room_id: int, db: Session = Depends(get_db)):
    chat_list = crud.find_chats_by_room(db=db, room_id=room_id)
    chat_list[0].contents = json.loads(gpt_util.get_completion(
        prompt="Reformat below input string to json. Response only formatted json. " + chat_list[0].contents))
    for i in range(1, len(chat_list)):
        chat_list[i].contents = chat_list[i].contents.split('\n\n')
    return {
        "chats": chat_list
    }
