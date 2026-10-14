from typing import AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Kiểm tra nếu đang dùng SQLite
_is_sqlite = "sqlite" in settings.DATABASE_URL


# Khởi tạo engine bất đồng bộ (Async Engine) phục vụ cho FastAPI Web API
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),
    future=True,
    # SQLite không hỗ trợ pool_pre_ping
    **({"pool_pre_ping": True} if not _is_sqlite else {}),
)

# Factory tạo phiên làm việc bất đồng bộ (AsyncSession)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Engine đồng bộ (Sync Engine) dùng cho Alembic migrations, Celery worker và tác vụ nền đồng bộ
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=False,
    **({"pool_pre_ping": True} if not _is_sqlite else {}),
)

# Bật WAL mode cho SQLite để hỗ trợ concurrent reads
if _is_sqlite:
    @event.listens_for(sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Factory tạo phiên làm việc đồng bộ (SyncSession)
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """
    Lớp cơ sở Declarative Base cho toàn bộ SQLAlchemy Models trong hệ thống C_Data
    """
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency cung cấp phiên làm việc cơ sở dữ liệu bất đồng bộ cho FastAPI endpoints.
    Tự động commit khi thành công và rollback khi xảy ra lỗi.
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


def get_sync_db():
    """
    Helper generator cung cấp phiên làm việc cơ sở dữ liệu đồng bộ cho Celery tasks.
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
