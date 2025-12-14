from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker)
from sqlalchemy.pool import NullPool
from .settings import Settings

settings = Settings()

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@order-db:5432/{settings.DATABASE}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncSession:
    """
    Provee una sesión de base de datos asíncrona.

    Uso típico:
        @app.post("/orders")
        async def create_order(
            order_data: OrderSchema,
            db: AsyncSession = Depends(get_async_session)
        ):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
