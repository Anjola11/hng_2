from sqlalchemy.ext.asyncio import create_async_engine
from src.config import Config
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker


engine = create_async_engine(
    url = Config.DATABASE_URL,
    echo = True
)

async def init_db():
    async with engine.begin() as conn:

        from src.countries.models import Country
        await conn.run_sync(SQLModel.metadata.create_all)


async_session_maker = sessionmaker(
    bind=engine,
    class_= AsyncSession,
    expire_on_commit=False
)

async def get_session():
    async with async_session_maker() as session:
        yield session