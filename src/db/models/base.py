from uuid import uuid4

from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class BaseModel(DeclarativeBase):
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.flush()
        return self

    async def delete(self, session: AsyncSession):
        await session.delete(self)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

        return self
