# Base service

This service is universal and you can create as many copies of it as you want. All you will be need to add - adresses of services in /main_project/backend/utils/async_requests.py.

The service is serving as database service, it gives access to its database in CRUD way and gives some other info (like indexes, that are used in this database to understand on which index we can create new data).

## Startup

0. Presuming you set up all things like .env, venv, etc.

1. cd third_data

2. python main.py
