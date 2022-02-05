from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta

import jwt
from jwt import PyJWTError

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse
from starlette.requests import Request as R

from ..utils.base_config import setup_db
from ..utils import schemas

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

database, _, users_base = setup_db()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)

async def get_this_user(username):
    query = users_base.select().where(users_base.columns.username==username)
    await database.connect()
    result = await database.execute(query)
    print(result)
    if not result:
        return {"error": "username is not in database"}

    data = await database.fetch_all(query)
    await database.disconnect()
    user = schemas.User(**data[0])
    return user


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: R) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                return None
                # raise HTTPException(
                #     status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                # )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/token")


def verify_password(plain_password, hashed_password):
    a = pwd_context.verify(plain_password, hashed_password)
    return a


# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return schemas.User(**user_dict)


async def authenticate_user(username: str, password: str):
    user = await get_this_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # credentials_exception = HTTPException(
    #     status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    # )
    # credentials_exception = RedirectResponse(url="/login")
    credentials_exception = None
    print(token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print("username " + username)
        if username is None:
            # raise credentials_exception
            return credentials_exception
        token_data = schemas.TokenData(username=username)
    except PyJWTError:
        print("error")
        # raise credentials_exception
        return credentials_exception
    # user = get_user(fake_users_db, username=token_data.username)
    user = await get_this_user(token_data.username)
    if user is None:
        # raise credentials_exception
        return credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
):
    print(current_user)
    if not current_user or (type(current_user) is dict and current_user['error']):
        return "not logged"
    # print(current_user)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def user_login(username, password):
    try:
        print("test")
        user = await authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect login or password")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )

        token = jsonable_encoder(access_token)
        response = RedirectResponse(url="/auth_ok")
        response.set_cookie(
            "Authorization",
            value=f"Bearer {token}",
            domain="dohako.com",
            httponly=True,
            max_age=1800,
            expires=1800,
        )

    except Exception as ex:
        print(ex)
        response = RedirectResponse(url="/login", status_code=304)
    
    return response
