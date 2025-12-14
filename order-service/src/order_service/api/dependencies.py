from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker)
from sqlalchemy.pool import NullPool

DATABASE_URL = "sqlite+aiosqlite:///test.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Muestra las consultas SQL en consola (solo desarrollo)
    poolclass=NullPool,  # Para SQLite evita problemas con conexiones
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
            await session.commit()  # Commit automático al finalizar
        except Exception:
            await session.rollback()  # Rollback automático en error
            raise
        finally:
            await session.close()
