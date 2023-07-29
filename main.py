from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import scheme
import crud
import database

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


@app.post("/signup")
async def member_sign_up(req: scheme.SignUpInfo, db: Session = Depends(get_db)):
    member = crud.create_member(member=req, db=db)
    return {
        "message": "Sign Up Request Successed.",
        "email": str(member.email)
    }
