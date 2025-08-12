from datetime import datetime, timezone
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from models import Users, Tokens, Transactions
from database import SessionLocal 
from .auth import get_current_user
from pathlib import Path
import os
import shutil
from cv_model.inference import evaluate_cleanliness


router = APIRouter(
    prefix='/ai',
    tags=['ai']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Session, Depends(get_current_user)]


@router.post("/evaluate-cleanliness")
async def evaluate_cleanliness_endpoint(
    pre_image: Annotated[UploadFile, File(...)],
    post_image: Annotated[UploadFile, File(...)],
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not Authorized")
    
    try:
        # Save uploaded files temporarily
        pre_image_path = Path(f"temp_{pre_image.filename}")
        post_image_path = Path(f"temp_{post_image.filename}")

        with open(pre_image_path, "wb") as buffer:
            shutil.copyfileobj(pre_image.file, buffer)
        with open(post_image_path, "wb") as buffer:
            shutil.copyfileobj(post_image.file, buffer)

        # Run evaluation
        total_score, class_scores = evaluate_cleanliness(pre_image_path, post_image_path)

        # Clean up temp files
        os.remove(pre_image_path)
        os.remove(post_image_path)
        
        # calculate tokens for the user
        user_model = db.query(Users).filter(Users.id == user.get('id')).first()
        if not user_model:
            raise HTTPException(status_code=404, detail="User not found")
        token_model = db.query(Tokens).filter(Tokens.owner_id == user.get('id')).first()
        if not token_model:
            raise HTTPException(status_code=404, detail="Tokens not found for user")
        token_model.amount += total_score/10  # Assuming 10 tokens for each evaluation
        db.add(token_model)
        
        db.commit() 
        #Add a transaction record
        transaction = Transactions(
        amount=token_model.amount,
        owner_id=user.get('id'),
        type='earned',
        created_at=datetime.now(timezone.utc),
        description=f"Your cleanliness evaluation earned you {total_score/10} tokens."
    )
        db.add(transaction)
        db.commit

        return {
            "total_cleanliness_score": total_score,
            "tokens_earned": total_score / 10
            #"cleanliness_score_per_class": class_scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    