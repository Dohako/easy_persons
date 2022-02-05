from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.utils.base_config import setup_db
from app.utils import schemas
from app.utils.security import get_password_hash
from asyncpg import exceptions
from loguru import logger

app = FastAPI()

database, persons_base, users_base = setup_db()

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

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/data")
async def get_data(request:Request): 
    query = persons_base.select()
    data = await database.fetch_all(query)
    sorted_data = sorted(data, key=lambda d: d["global_id"])

    return sorted_data

@app.post("/data", status_code=201)
async def insert_person(person: schemas.Person):
    query = users_base.insert().values(
        username=person.username,
        global_id=person.global_id,
        hashed_password=get_password_hash("123"),
        status=person.status,
        disabled=False,
    )
    try:
        await database.execute(query)
    except exceptions.UniqueViolationError:
        return {"error":"this username is already taken"}

    query = persons_base.insert().values(
        first_name=person.first_name,
        last_name=person.last_name,
        username=person.username,
        email=person.email,
        status=person.status,
        global_id=person.global_id,
        disabled=False,
    )
    await database.execute(query)

    return {"success":"1"}


@app.post("/data", status_code=201)
async def register_person(create_user: schemas.User):
    query = users_base.insert().values(
        username=create_user.username,
        hashed_password=create_user.hashed_password,
        status=create_user.status,
        global_id=create_user.global_id,
        disabled=create_user.disabled,
    )
    try:
        await database.execute(query)
    except exceptions.UniqueViolationError:
        return {"error":"this username is already taken"}
    query = persons_base.insert().values(
        username=create_user.username,
        global_id=create_user.global_id,
        status=create_user.status,
        disabled=create_user.disabled,
    )
    await database.execute(query)

    return {"success":"1"}


@app.put("/data")
async def update_person(person: schemas.Person):
    logger.info("updating")
    logger.info(person)
    person_id = person.global_id
    query = persons_base.select().where(persons_base.columns.global_id == int(person_id))
    current_person = await database.fetch_one(query)

    print(person)

    for key, item in person.__dict__.items():
        if not item:
            person.__dict__[f"{key}"] = current_person.get(f"{key}")
    
    query = (
        users_base.update()
        .values(
            username=person.username,
            status=person.status,
            global_id=person.global_id
        )
        .where(users_base.columns.global_id == int(person_id))
    )
    try:
        await database.execute(query)
    except exceptions.UniqueViolationError:
        print("username error")
        return {"error":"this username is already taken"}
    query = (
        persons_base.update()
        .values(
            first_name=person.first_name,
            last_name=person.last_name,
            email=person.email,
            username=person.username,
            status=person.status,
            global_id=person.global_id,
        )
        .where(persons_base.columns.global_id == int(person_id))
    )
    try:
        await database.execute(query)
    except exceptions.UniqueViolationError:
        print("username error")
        return {"error":"this username is already taken"}
    return await database.execute(query)

@app.delete("/data/{person_id}", status_code=200)
async def delete_person(person_id: str):
    delete = persons_base.delete().where(persons_base.columns.global_id == int(person_id))
    await database.execute(delete)

    delete = users_base.delete().where(users_base.columns.global_id == int(person_id))
    await database.execute(delete)

    return {"success":"1"}


@app.get("/global_id")
async def get_max_global_id():
    query = persons_base.select()
    data = await database.fetch_all(query)
    sorted_data = sorted(data, key=lambda d: d["global_id"])
    test = ''
    for data in sorted_data:
        test = test + ', ' + str(data.get("global_id"))
    return test