from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session
import traceback
from asyncio import Lock
from models import *


lock = Lock()
Base = declarative_base()
engine = create_engine("sqlite:///data/database.sqlite3")


def create_tables():
    Base.metadata.create_all(engine)


def lock_and_release(func):
    async def wrapper(*args, **kwargs):
        try:
            await lock.acquire()
            s = Session(bind=engine, autoflush=True)
            result = await func(*args, **kwargs, s=s)
            s.commit()
            if result:
                return result
        except Exception as e:
            print(e)
            with open("errors.txt", "a", encoding="utf-8") as f:
                f.write(f"{traceback.format_exc()}\n{'-'*100}\n\n\n")
        finally:
            s.close()
            lock.release()

    return wrapper


def connect_and_close(func):
    def wrapper(*args, **kwargs):
        s = Session(bind=engine, autoflush=True)
        result = func(*args, **kwargs, s=s)
        s.close()
        return result

    return wrapper


from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
