from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(
    "postgresql+asyncpg://pizza:hjuLwoEU6mspTMOUVfYQNiP6EW4Ac5Ml@dpg-ctbmtl56l47c73b2tslg-a.frankfurt-postgres.render.com/pizza_bw1h", echo=True
)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
