# easy_persons

This is my implementation of system, that allow controll access for different persons to admin/user info and actions.

This system is using 3 databases that it reaching through API. Bases can be whatever you want, for the project it is a psql.

## Main stack

* fastapi
* uvicorn
* sqlalchemy
* asyncio
* asyncpg
* loguru
* httpx

## Instructions (Presuming Windows)

0. create databases in local psql (persons_first, persons_second, persons_third -> empty)

1. If you will run services on localhost - you will need to change your hosts file (google please about it) to redirect requests from 'dohako.com' to your localhost. Also you can create it by your desired name, but you will need to change adresses on front side and inside code (Will think of method to easy change it)

2. `git clone url` -> cd to it

3. fill .env.dev and rename to .env inside each *_data folder

4. `python -m venv venv`

5. `venv\Scripts\activate.bat`

6. `pip install -r requirements.txt`

7. main process

    1. cd backend

    2. python main.py

8. database 1

    1. cd first_data

    2. python main.py

9. database 2

    1. cd second_data

    2. python main.py

10. database 3

    1. cd third_data

    2. python main.py

## Working (presuming you stayed with my preferences)

1. go to dohako.com:8000/home or .../login (doesn't matter, cause you will get redirected to /login)

2. type your username and pass (don't forget it or you will need to erase bases, it's also TBD)

3. press register button and if username is not taken - you will create user

4. next press on login button

5. first one to register in databases will become Admin, others firstly become users

### Admin

1. If you are an admin you will see list of users and you can delete anyone (even yourself, but be careful with it)

2. You can create new users/persons in top of page

3. You can Edit anyone by Global ID (even yourself, but don't forget to manage status to admin)

4. All users/persons (admins or not) that you will create here CAN login to service through pass "123" (yes, it's not best, change pass is tbd)

5. there is also a logout button

### User

1. If you are a user you will just see list of other users, nothing else

2. there is a logout button

## TBD

* change pass

* pass check

* ...

## Работа

* ~~форма~~
* ~~ajax~~
* ~~апи~~
* ~~логин~~
* ~~одна база~~
* ~~токен~~
* ~~разные формы для админа/пользователя~~
* ~~одна база -> три базы~~
