from fastapi import FastAPI, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from typing import List
from loguru import logger
from asyncpg import exceptions

from .utils import schemas
from .utils.base_config import setup_db
from .utils.async_requests import set_async_request
from .utils.security import user_login, get_current_active_user, get_password_hash
from .utils.d_utils import list_from_list_of_lists


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


@app.get("/home", response_model=List[schemas.Person], response_class=HTMLResponse)
async def read_persons(request: Request, current_user=Depends(get_current_active_user)):
    if current_user == "not logged":
        logger.error(current_user)
        response = RedirectResponse(url="/login")
        return response
    # check what's going on when depends returning redirect
    if current_user.status == "admin":
        page = "home.html"
    else:
        page = "user_home.html"

    a = await set_async_request(request_type="get")
    temp_result = list_from_list_of_lists(a)

    template = templates.TemplateResponse(
        page,
        {
            "request": request,
            "persons": sorted(temp_result, key=lambda d: d["global_id"]),
        },
    )
    return template


# create update delete


@app.post("/person")
async def insert_person(person: schemas.Person):
    await set_async_request(data=person, request_type="post")
    return {"success": "1"}


@app.put("/person/{person_id}")
async def update_person(person_id: str, person: schemas.Person):
    logger.info(f"updating {person}")
    await set_async_request(data=person, request_type="put")
    return {"success": "1"}


@app.delete("/person/{person_id}", status_code=200)
async def delete_person(person_id: str):
    logger.info(person_id)
    await set_async_request(person_id=person_id, request_type="delete")
    return {"success": "1"}
