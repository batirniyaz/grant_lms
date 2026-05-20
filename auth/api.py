from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth.schema import (Token, UserRead)
from auth.util import (authenticate_user, create_access_token, oauth2_scheme, blacklist_token, read_me, UserDep, AdminDep)
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from db.get_db import SessionDep

router = APIRouter()




@router.post("/login")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: SessionDep,
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "role": user.role.value,
            "phone": user.phone,
            "email": user.email,
        },
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(current_user: UserDep, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    await blacklist_token(token, db)
    return {"msg": "Successfully logged out"}


@router.get("/me/", response_model=UserRead)
async def read_user_me(current_user: UserDep, db: SessionDep):
    user = await read_me(db, current_user)
    return UserRead.model_validate(user)


