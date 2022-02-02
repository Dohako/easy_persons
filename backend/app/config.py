import databases
import sqlalchemy


def setup_db():
    DATABASE_URL = "postgresql://postgres:92292400Sql@localhost/persons"

    database = databases.Database(DATABASE_URL)

    metadata = sqlalchemy.MetaData()

    persons = sqlalchemy.Table(
        "persons",
        metadata,
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("first_name", sqlalchemy.String),
        sqlalchemy.Column("last_name", sqlalchemy.String),
        sqlalchemy.Column("email", sqlalchemy.String),
        sqlalchemy.Column("status", sqlalchemy.String),
    )

    users = sqlalchemy.Table(
        "users",
        metadata,
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("login", sqlalchemy.String),
        sqlalchemy.Column("password", sqlalchemy.String),
        sqlalchemy.Column("status", sqlalchemy.String),
    )


    engine = sqlalchemy.create_engine(
        DATABASE_URL
    )
    metadata.create_all(engine)

    return database, persons, users
