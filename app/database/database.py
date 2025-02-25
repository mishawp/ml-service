from sqlmodel import SQLModel, Session, create_engine, text
from .config import get_settings

engine = create_engine(
    url=get_settings().DATABASE_URL_psycopg,
    echo=False,
    # echo=True,
    pool_size=5,
    max_overflow=10,
)


def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    # SQLModel.metadata.drop_all(engine)
    with engine.connect() as connection:
        connection.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
        connection.execute(text('DROP TABLE IF EXISTS "admin" CASCADE'))
        connection.execute(text("DROP TABLE IF EXISTS payment CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS chat CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS cost CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS prediction CASCADE"))
        connection.commit()
    SQLModel.metadata.create_all(engine)
