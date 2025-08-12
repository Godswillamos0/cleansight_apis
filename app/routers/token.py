from datetime import datetime, timezone
from typing import Annotated
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from models import Users, Tokens, Transactions
from database import SessionLocal 
from .auth import get_current_user


router = APIRouter(
    prefix='/token',
    tags=['token']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Session, Depends(get_current_user)]


class DonateTokensRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount of tokens to donate, must be greater than 0")
    #id: Optional[int] = Field(None, description="ID of the user that donated tokens. If not provided, the current user's ID will be used.")
    description: Optional[str] = Field(None, description="Description of the donation, optional")


@router.get('/balance', status_code=200)
async def get_balance(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not Authorized')
    
    user_model = db.query(Users).filter(Users.id==user.get('id')).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    token_model = db.query(Tokens).filter(Tokens.owner_id==user.get('id')).first()
    if not token_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tokens not found for user')
    
    return {
        "balance": token_model.amount
    }
    
    
@router.post('/donate', status_code=status.HTTP_201_CREATED)
async def add_tokens(user: user_dependency, db: db_dependency, dnt: DonateTokensRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not Authorized')
    
    user_model = db.query(Users).filter(Users.id==user.get('id')).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    token_model = db.query(Tokens).filter(Tokens.owner_id==user.get('id')).first()
    if not token_model:
        token_model = Tokens(owner_id=user.get('id'), amount=0.0)
     
    if token_model.amount < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Insufficient token balance')
    
    if dnt.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Amount must be greater than 0')
    if dnt.amount > token_model.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot donate more tokens than available')
    
    token_model.amount -= dnt.amount
    db.add(token_model)
    db.commit()
    #Add a transaction record
    transaction = Transactions(
        amount=dnt.amount,
        owner_id=user.get('id'),
        type='donation',
        created_at=datetime.now(timezone.utc),
        description=dnt.description if dnt.description else None
    )
    db.add(transaction)
    db.commit()
    
    return {
        "message": "Tokens added successfully",
        "new_balance": token_model.amount
    }
    
    
@router.get('/transactions', status_code=status.HTTP_200_OK)
async def get_transactions(
    user: user_dependency, db: db_dependency,
    page: int = Query(1, ge=1),          # Page number, default 1
    page_size: int = Query(20, ge=1, le=100)  # Results per page, default 20, max 100
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Not Authorized'
        )
    
    # Sort by latest first (assuming you have a `created_at` column)
    query = (
        db.query(Transactions).filter(Transactions.owner_id == user.get('id'))
        .order_by(Transactions.created_at.desc())  # newest first
    )

    total_count = query.count()  # total transactions for this user

    # Pagination logic
    transactions = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='No transactions found for user'
        )

    return {
        "page": page,
        "page_size": page_size,
        "total_transactions": total_count,
        "transactions": transactions
    }
