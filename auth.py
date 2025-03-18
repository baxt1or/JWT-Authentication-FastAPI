from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from schemas import CreateUserRequest, Token, LoginRequest
from database import get_db


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = "4f4d55cfd55f4a74b787a2e4c59e73512a1d6cb21b6f8e23d0c9b9c03b8b967b" 
ALGORITHM = "HS256"  
ACCESS_TOKEN_EXPIRE_MINUTES = 30 


bcrypt_context = CryptContext(schemes=['bcrypt'])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user:CreateUserRequest,db:db_dependency):

    hash_password = bcrypt_context.hash(user.password)

    new_user = Users(username=user.username, hashed_password=hash_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message":f"Successfully created user with {new_user.username}"}



def get_user(db, username, password):

    user = db.query(Users).filter(Users.username == username).first()

    if not user or not  bcrypt_context.verify(password, user.hashed_password):
        print("No Users")
        return None
    
    return user

def create_access_token(username:str, user_id:int, expires_delta : timedelta):
    
    encode = {'sub':username, 'id':user_id}
    expires = datetime.utcnow()+expires_delta
    encode.update({'exp':expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token", response_model=Token)
async def login(db:db_dependency, form_data : Annotated[OAuth2PasswordRequestForm, Depends()]):

    user = get_user(db=db, password=form_data.password, username=form_data.username)

    if not user:
        raise HTTPException(detail="Failed to find a user", status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = create_access_token(username=user.username, user_id=user.id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return {"access_token": token, "token_type":"bearer"}

    
async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get('sub')
        user_id: str = payload.get('id')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')
        
        return {'username':username, 'id':user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')
            
