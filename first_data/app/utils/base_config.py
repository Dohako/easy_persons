import databases
import sqlalchemy
from ..utils.d_utils import PsqlEnv


def setup_db():
    """
    Get env vars and create db if they don't exists
    returns database object and tables objects
    """
    env = PsqlEnv()
    DATABASE_URL = env.get_env_url()

    database = databases.Database(DATABASE_URL)

    metadata = sqlalchemy.MetaData()

    persons = sqlalchemy.Table(
        "persons",
        metadata,
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("global_id", sqlalchemy.Integer),
        sqlalchemy.Column("first_name", sqlalchemy.String),
        sqlalchemy.Column("last_name", sqlalchemy.String),
        sqlalchemy.Column("username", sqlalchemy.String, unique=True),
        sqlalchemy.Column("email", sqlalchemy.String),
        sqlalchemy.Column("status", sqlalchemy.String),
        sqlalchemy.Column("disabled", sqlalchemy.Boolean),
    )

    users = sqlalchemy.Table(
        "users",
        metadata,
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("global_id", sqlalchemy.Integer),
        sqlalchemy.Column("username", sqlalchemy.String, unique=True),
        sqlalchemy.Column("hashed_password", sqlalchemy.String, nullable=False),
        sqlalchemy.Column("status", sqlalchemy.String),
        sqlalchemy.Column("disabled", sqlalchemy.Boolean),
    )

    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)

    return database, persons, users
