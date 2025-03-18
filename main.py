from fastapi import FastAPI, Depends, HTTPException
from starlette import status
from database import Base, engine, get_db
from sqlalchemy.orm import Session
from typing import Annotated
from auth import router, get_current_user

app = FastAPI()
app.include_router(router=router)


Base.metadata.create_all(bind=engine)


db_dependency = Annotated[Session, Depends(get_db)]
user_credentials = Annotated[dict, Depends(get_current_user)]

@app.get("/")
async def get_users(user: user_credentials):

    print(user)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    return {"user":user}
    
