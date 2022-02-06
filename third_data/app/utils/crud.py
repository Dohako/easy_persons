from ..utils import schemas
from ..utils.base_config import setup_db
from ..utils.security import get_password_hash
from asyncpg import exceptions


class BaseHandler:
    def __init__(self) -> None:
        self.database, self.persons_base, self.users_base = setup_db()

    async def start(self):
        await self.database.connect()

    async def stop(self):
        await self.database.disconnect()

    async def get_data(self, request):
        """
        :param: request - depricated, to be erased in future
        """
        query = self.persons_base.select()
        data = await self.database.fetch_all(query)
        sorted_data = sorted(data, key=lambda d: d["global_id"])

        return sorted_data

    async def get_by_user_id(self, user: schemas.User):
        # first check if username exists
        query = self.users_base.select().where(
            self.users_base.columns.username == user.username
        )
        result = await self.database.execute(query)
        if not result:
            return {"error": "username is not in database"}
        # then return user data if exists
        data = await self.database.fetch_all(query)
        user = schemas.User(**data[0])
        return user

    async def insert_person_from_front(self, person: schemas.Person):
        query = self.users_base.insert().values(
            username=person.username,
            global_id=person.global_id,
            hashed_password=get_password_hash("123"),
            status=person.status,
            disabled=False,
        )
        try:
            await self.database.execute(query)
        except exceptions.UniqueViolationError:
            return {"error": "this username is already taken"}

        query = self.persons_base.insert().values(
            first_name=person.first_name,
            last_name=person.last_name,
            username=person.username,
            email=person.email,
            status=person.status,
            global_id=person.global_id,
            disabled=False,
        )
        await self.database.execute(query)

        return {"success": "1"}

    async def register_person(self, create_user: schemas.User):
        query = self.users_base.insert().values(
            username=create_user.username,
            hashed_password=create_user.hashed_password,
            status=create_user.status,
            global_id=create_user.global_id,
            disabled=create_user.disabled,
        )
        try:
            await self.database.execute(query)
        except exceptions.UniqueViolationError:
            return {"error": "this username is already taken"}
        query = self.persons_base.insert().values(
            username=create_user.username,
            global_id=create_user.global_id,
            status=create_user.status,
            disabled=create_user.disabled,
        )
        await self.database.execute(query)

        return {"success": "1"}

    async def update_person(self, person: schemas.Person):
        person_id = person.global_id
        query = self.persons_base.select().where(
            self.persons_base.columns.global_id == int(person_id)
        )
        current_person = await self.database.fetch_one(query)

        print(person)

        for key, item in person.__dict__.items():
            if not item:
                person.__dict__[f"{key}"] = current_person.get(f"{key}")

        query = (
            self.users_base.update()
            .values(
                username=person.username,
                status=person.status,
                global_id=person.global_id,
            )
            .where(self.users_base.columns.global_id == int(person_id))
        )
        try:
            await self.database.execute(query)
        except exceptions.UniqueViolationError:
            print("username error")
            return {"error": "this username is already taken"}
        query = (
            self.persons_base.update()
            .values(
                first_name=person.first_name,
                last_name=person.last_name,
                email=person.email,
                username=person.username,
                status=person.status,
                global_id=person.global_id,
            )
            .where(self.persons_base.columns.global_id == int(person_id))
        )
        try:
            await self.database.execute(query)
        except exceptions.UniqueViolationError:
            print("username error")
            return {"error": "this username is already taken"}

        await self.database.execute(query)

        return {"success": "1"}

    async def delete_person(self, person_id: str):

        delete = self.persons_base.delete().where(
            self.persons_base.columns.global_id == int(person_id)
        )
        await self.database.execute(delete)

        delete = self.users_base.delete().where(
            self.users_base.columns.global_id == int(person_id)
        )
        await self.database.execute(delete)

        return {"success": "1"}

    async def get_max_global_id(self):
        query = self.persons_base.select()
        data = await self.database.fetch_all(query)
        sorted_data = sorted(data, key=lambda d: d["global_id"])
        global_ids = ""
        for data in sorted_data:
            global_ids = global_ids + ", " + str(data.get("global_id"))
        return global_ids
