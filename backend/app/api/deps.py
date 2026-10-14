from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

# Type alias tiện lợi cho việc inject AsyncSession vào các endpoint FastAPI
SessionDep = Annotated[AsyncSession, Depends(get_db)]

__all__ = ["get_db", "SessionDep"]
