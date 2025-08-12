from typing import Annotated, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import SessionLocal 
from .auth import get_current_user


router = APIRouter(
    prefix= '/user',
    tags=['user']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Session, Depends(get_current_user)]


class PasswordRequest(BaseModel):
    password: str
    new_password: str


@router.get('/', status_code=200)
async def get_user(user: user_dependency,
                   db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not Authorized')
    
    user_model = db.query(Users).filter(Users.id==user.get('id')).first()
    return {
        "email": user_model.email,
        "username": user_model.username,
        "first_name": user_model.first_name,
        "last_name": user_model.last_name
        }

@router.post('/change_password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          password_request: PasswordRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id==user.get('id')).first()

    if not bcrypt_context.verify(password_request.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error in password change')
    user_model.hashed_password = bcrypt_context.hash(password_request.new_password)
    db.add(user_model)
    db.commit()


@router.get('/all_users', status_code=200)
async def get_all_user(db: db_dependency):
    user_model = db.query(Users).all()
    return user_model