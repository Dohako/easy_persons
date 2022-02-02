from tkinter import EXCEPTION
from fastapi import FastAPI, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from .utils import schemas
from .config import setup_db
import databases

##
from typing import Optional
import base64
from passlib.context import CryptContext
from datetime import datetime, timedelta

import jwt
from jwt import PyJWTError

from pydantic import BaseModel

from fastapi import Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.utils import get_openapi

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, Response, JSONResponse
from starlette.requests import Request as R
import starlette.status as status
##


def test_iter():
    for i in range(100):
        yield i


app = FastAPI()

list_of_usernames = list()
templates = Jinja2Templates(directory="backend/app/templates")


origins = [
    "http://localhost:3000",
    "localhost:3000",
    "http://localhost:8080",
    "localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database, persons_base, users_base = setup_db()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Login part

# login test



# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    print(password)
    return pwd_context.hash(password)

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        # "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "hashed_password": f"{get_password_hash('123')}",
        "disabled": False,
    }
}




class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    disabled: bool = None


class UserInDB(User):
    hashed_password: str


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
                # return None
                # print(scheme.lower())
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param


class BasicAuth(SecurityBase):
    def __init__(self, scheme_name: str = None, auto_error: bool = True):
        self.scheme_name = scheme_name or self.__class__.__name__
        self.model = SecurityBase()
        self.auto_error = auto_error

    async def __call__(self, request: R) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "basic":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param



oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/token")

# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


def verify_password(plain_password, hashed_password):
    a = pwd_context.verify(plain_password, hashed_password)
    print(a)
    return a

# def get_password_hash(password):
#     print(password)
#     return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    print(user)
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
    credentials_exception = HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            # return None
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        # return None
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    print(123)
    if user is None:
        # return None
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user:
        return "not logged"
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def route_login_access_token(username: str | None = Form(...), password: str | None = Form(...)):
    user = authenticate_user(fake_users_db, username, password)
    print("*"*100)
    print(user)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/logout")
async def route_logout_and_remove_cookie():
    # why i cant get ajax success from response?
    response = RedirectResponse(url="/login_out")
    response.delete_cookie("Authorization", domain="dohako.com")
    return response

@app.get("/login_out")
async def logout_user():
    # temp function to return success for ajax
    return {"success": "1"}

@app.post("/auth_ok")
async def auth_user():
    # temp function to return success for ajax
    return {"success": "1"}

@app.post("/auth")
async def login_basic(username: str | None = Form(...), password: str | None = Form(...)):
    # if not auth:
    #     response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
    #     return response
    # username = 1
    # password = 1

    print(username)
    try:
        user = authenticate_user(fake_users_db, username, password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        print(1)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        print(2)
        token = jsonable_encoder(access_token)
        print(3)
        response = RedirectResponse(url="/auth_ok")
        print(4)
        response.set_cookie(
            "Authorization",
            value=f"Bearer {token}",
            domain="dohako.com",
            httponly=True,
            max_age=1800,
            expires=1800,
        )
        print(5)
        # return {"success": "1", "response": response}
        return response

    except Exception as ex:
        print(ex)
        # response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        response = RedirectResponse(url="/login")
        return response


# @app.get("/openapi.json")
# async def get_open_api_endpoint(current_user: User = Depends(get_current_active_user)):
#     return JSONResponse(get_openapi(title="FastAPI", version=1, routes=app.routes))


# @app.get("/docs")
# async def get_documentation(current_user: User = Depends(get_current_active_user)):
#     return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


# @app.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user


# @app.get("/users/me/items/")
# async def read_own_items(current_user: User = Depends(get_current_active_user)):
#     return [{"item_id": "Foo", "owner": current_user.username}]

# login test end

# @app.post("/auth", status_code=200)
# async def auth_user(username: str | None = Form(...), password: str | None = Form(...)):
#     if username:
#         return {"success": "1"}
#     else:
#         return {"success": "0"}


@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# main

@app.get("/home", response_model=List[schemas.Person], response_class=HTMLResponse)
async def read_persons(request: Request, current_user: User = Depends(get_current_active_user)):
    print(current_user)
    if current_user == "not logged":
        response = RedirectResponse(url="/login")
        return response
    query = persons_base.select()
    # print(current_user)
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "persons": sorted(await database.fetch_all(query), key=lambda d: d["id"]),
        },
    )

# create update delete

@app.post("/person", status_code=201)
async def insert_person(person: schemas.CreatePerson):
    query = persons_base.insert().values(
        first_name=person.first_name,
        last_name=person.last_name,
        email=person.email,
        status=person.status,
    )
    last_record_id = await database.execute(query)
    return {**person.dict(), "id": last_record_id}


@app.put("/person/{person_id}")
async def update_person(person_id: str, person: schemas.UpdatePerson):
    query = persons_base.select().where(persons_base.columns.id == int(person_id))
    current_person = await database.fetch_one(query)

    for key, item in person.__dict__.items():
        if not item:
            person.__dict__[f"{key}"] = current_person.get(f"{key}")

    query = (
        persons_base.update()
        .values(
            first_name=person.first_name,
            last_name=person.last_name,
            email=person.email,
            status=person.status,
        )
        .where(persons_base.columns.id == int(person_id))
    )
    return await database.execute(query)


@app.delete("/person/{person_id}", status_code=200)
async def delete_person(person_id: str):
    delete = persons_base.delete().where(persons_base.columns.id == int(person_id))
    return await database.execute(delete)
