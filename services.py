from models import Users
from auth import bcrypt_context
from datetime import timedelta, datetime
from jose import JWTError, jwt

SECRET_KEY = "4f4d55cfd55f4a74b787a2e4c59e73512a1d6cb21b6f8e23d0c9b9c03b8b967b" 
ALGORITHM = "HS256"  
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

def get_user(db, username, password):

    user = db.query(Users).filter(Users.email == username).first()

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return user

def create_access_token(username:str, user_id:int, expires_delta : timedelta):
    
    encode = {'sub':username, 'id':user_id}
    expires = datetime.utcnow()+expires_delta
    encode.update({'exp':expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)