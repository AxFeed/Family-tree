from sqlmodel import create_engine, Session
from typing import Generator

DATABASE_URL = "mysql+pymysql://bob:ross@localhost:3306/BobFamily"

engine = create_engine(DATABASE_URL)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
