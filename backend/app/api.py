from fastapi import FastAPI, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Tuple

from fastapi_users_db_sqlalchemy import delete
import sqlalchemy
from .utils import schemas
from .utils.base_config import setup_db
from .utils.async_requests import (
    set_async_request,
    set_async_id_retrieve,
    get_first_missing_global_id,
)
from asyncpg import exceptions

##
from .utils.security import user_login, get_current_active_user, get_password_hash
from starlette.responses import RedirectResponse
import json
from loguru import logger

##


app = FastAPI()

list_of_usernames = list()
templates = Jinja2Templates(directory="app/templates")


origins = [
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
async def login_basic(
    username: str | None = Form(...), password: str | None = Form(...)
):
    return await user_login(username, password)


@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

    # here i need to get vals from dict and sort and find max


# async def get_max_global_id():
#     query = persons_base.select()
#     data = await database.fetch_all(query)
#     sorted_data = sorted(data, key=lambda d: d["global_id"])
#     test = []
#     for data in sorted_data:
#         test.append(data.get("global_id"))
#     return test
# print(first_missing_number(test))


@app.post("/register")
async def register(create_user: schemas.User):
    print(create_user)

    first_row_query = users_base.select().where(users_base.columns.id == 1)
    first_row = await database.execute(first_row_query)

    # data = await database.fetch_all(first_row_query)
    # # a,b,c,d,e,f = **data[0]
    # a = schemas.UserInDB(**data[0])
    # print(a)

    if first_row:
        create_user.status = "user"
    else:
        create_user.status = "admin"
    # TBD check user exists
    create_user.hashed_password = get_password_hash(create_user.hashed_password)
    create_user.disabled = False

    await set_async_request(data=create_user, request_type="post")

    query = users_base.insert().values(
        username=create_user.username,
        hashed_password=create_user.hashed_password,
        global_id=create_user.global_id,
        status=create_user.status,
        disabled=create_user.disabled,
    )
    try:
        await database.execute(query)
    except exceptions.UniqueViolationError:
        return {"error": "this username is already taken"}
    query = persons_base.insert().values(
        username=create_user.username,
        global_id=create_user.global_id,
        status=create_user.status,
        disabled=create_user.disabled,
    )
    await database.execute(query)

    return {"success": "1"}


@app.post("/change_pass")
async def change_pass():
    ...


# main


def list_from_list_of_lists(some_list: list):
    test = [item for sublist in some_list for item in sublist]
    return test


@app.get("/home", response_model=List[schemas.Person], response_class=HTMLResponse)
async def read_persons(request: Request, current_user=Depends(get_current_active_user)):
    if current_user == "not logged":
        print("not logged")
        response = RedirectResponse(url="/login")
        return response
    # check what's going on when depends returning redirect
    if current_user.status == "admin":
        page = "home.html"
    else:
        page = "user_home.html"

    a = await set_async_request(request_type="get")
    temp_result = list_from_list_of_lists(a)

    query = persons_base.select()
    data = await database.fetch_all(query)
    # sorted_data = sorted(data, key=lambda d: d["id"])
    sorted_data = sorted(data, key=lambda d: d["global_id"])
    template = templates.TemplateResponse(
        page,
        {
            "request": request,
            "persons": sorted(temp_result, key=lambda d: d["global_id"]),
        },
    )
    return template


# async calls


# create update delete


@app.post("/person")
async def insert_person(person: schemas.Person):

    await set_async_request(data=person, request_type="post")

    # query = users_base.insert().values(
    #     username=person.username,
    #     hashed_password=get_password_hash("123"),
    #     global_id=person.global_id,
    #     status=person.status,
    #     disabled=False,
    # )
    # try:
    #     await database.execute(query)
    # except exceptions.UniqueViolationError:
    #     return {"error": "this username is already taken"}

    # query = persons_base.insert().values(
    #     first_name=person.first_name,
    #     last_name=person.last_name,
    #     username=person.username,
    #     email=person.email,
    #     status=person.status,
    #     global_id=person.global_id,
    #     disabled=False,
    # )
    # last_record_id = await database.execute(query)

    # forgot why I returned id... To be checked
    # return {**person.dict(), "id": last_record_id}
    return {"success": "1"}


@app.put("/person/{person_id}")
async def update_person(person_id: str, person: schemas.Person):

    logger.info("updating")
    logger.info(person)
    await set_async_request(data=person, request_type="put")

    # query = persons_base.select().where(persons_base.columns.id == int(person_id))
    # current_person = await database.fetch_one(query)

    # print(person)

    # for key, item in person.__dict__.items():
    #     if not item:
    #         person.__dict__[f"{key}"] = current_person.get(f"{key}")

    # query = (
    #     users_base.update()
    #     .values(
    #         username=person.username,
    #         status=person.status,
    #     )
    #     .where(users_base.columns.id == int(person_id))
    # )
    # try:
    #     await database.execute(query)
    # except exceptions.UniqueViolationError:
    #     print("username error")
    #     return {"error": "this username is already taken"}
    # query = (
    #     persons_base.update()
    #     .values(
    #         first_name=person.first_name,
    #         last_name=person.last_name,
    #         email=person.email,
    #         username=person.username,
    #         status=person.status,
    #         global_id=person.global_id,
    #     )
    #     .where(persons_base.columns.id == int(person_id))
    # )
    # try:
    #     await database.execute(query)
    # except exceptions.UniqueViolationError:
    #     print("username error")
    #     return {"error": "this username is already taken"}

    return {"success": "1"}


@app.delete("/person/{person_id}", status_code=200)
async def delete_person(person_id: str):
    logger.info(person_id)

    await set_async_request(person_id=person_id, request_type="delete")

    return {"success": "1"}
