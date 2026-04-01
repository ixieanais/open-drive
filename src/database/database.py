from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy_utils import create_database, database_exists  # , drop_database

from config import DATABASE_URL, DATABASE_URL_UTILS


engine = create_async_engine(url=DATABASE_URL, echo=False)


# drop_database(DATABASE_URL_UTILS) # if you need to drop a database
if not database_exists(DATABASE_URL_UTILS):
    create_database(DATABASE_URL_UTILS)


session_factory = async_sessionmaker(engine)
