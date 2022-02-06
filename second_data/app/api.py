from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.utils import schemas
from app.utils.crud import BaseHandler

app = FastAPI()

base = BaseHandler()

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
    await base.start()


@app.on_event("shutdown")
async def shutdown():
    await base.stop()


# GET


@app.get("/data")
async def get_data(request: Request):
    """
    get all data in sorted way
    """
    sorted_data = await base.get_data(request)
    return sorted_data


@app.get("/global_id")
async def get_max_global_id():
    """
    get list of ids that present in current base
    """
    global_ids = await base.get_max_global_id()
    return global_ids


# POST


@app.post("/get_by_user_id")
async def get_by_user_id(user: schemas.User):
    """
    this request is get, but I made it post because I need to transfer data in more protected way, than
    get allows (through uri is poor)
    This request need for auth purposes, it checks for a user in db and send back neither error or User
    """
    user = await base.get_by_user_id(user)
    return user


@app.post("/data", status_code=201)
async def insert_person(person: schemas.Person):
    """
    this request comes on inserting person from admin panel
    in that case we give a person simple pass => 123
    """
    await base.insert_person_from_front(person)
    return {"success": "1"}


@app.post("/register", status_code=201)
async def register_person(create_user: schemas.User):
    """
    this request comes from register button on /login
    in that case we take pass from form
    """
    await base.register_person(create_user)
    return {"success": "1"}


# PUT


@app.put("/data")
async def update_person(person: schemas.Person):
    """
    updating existing person
    """
    await base.update_person(person)
    return {"success": "1"}


# DELETE


@app.delete("/data/{person_id}", status_code=200)
async def delete_person(person_id: str):
    """
    deleting existing person
    """
    await base.delete_person(person_id)
    return {"success": "1"}
