from fastapi import FastAPI, Body, Request, File, UploadFile, Form
from fastapi import responses
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()

list_of_usernames = list()
templates = Jinja2Templates(directory="backend/app/templates")


class NameValues(BaseModel):
    name: str = None
    country: str
    age: int
    base_salary: float

origins = [
    "http://localhost:3000",
    "localhost:3000",
    "http://localhost:8080",
    "localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to test of new way in developing desktop"}

@app.post("/auth")
async def auth_user(username: str | None = Form(...), password: str | None = Form(...)):
    print(username, password)
    if username:
        return True
    else:
        return False

@app.get("/home", response_class=HTMLResponse)
def write_home(request:Request):
    return templates.TemplateResponse("login.html", {"request":request})
