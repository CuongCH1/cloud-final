from typing import Generic, Type, TypeVar

from sqlalchemy import ColumnClause, asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def create(self, obj: T) -> T:
        obj = await obj.save(self.session)
        await self.session.commit()
        return obj

    async def get(self, id: str) -> T | None:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: str | None = None,
        ascending: bool = True,
        **kwargs,
    ) -> list[T]:
        filters = self._create_filters(**kwargs)

        stmt = select(self.model).where(*filters).offset(offset).limit(limit)

        if sort_by is not None and hasattr(self.model, sort_by):
            order_by = asc(sort_by) if ascending else desc(sort_by)
            stmt = stmt.order_by(order_by)

        result = await self.session.execute(stmt)
        result = [*result.scalars().all()]

        return result

    async def find_one(self, **kwargs) -> T | None:
        filters = self._create_filters(**kwargs)
        stmt = select(self.model).where(*filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, id: str, **kwargs) -> T | None:
        todo = await self.get(id)

        if not todo:
            return None

        todo = todo.update(**kwargs)
        await self.session.commit()
        await self.session.refresh(todo)

        return todo

    async def delete(self, id: str) -> T | None:
        todo = await self.get(id)

        if not todo:
            return None

        await todo.delete(self.session)
        await self.session.commit()

        return todo

    def _create_filters(self, **kwargs) -> list[ColumnClause]:
        filters: list[ColumnClause] = []

        for k, v in kwargs.items():
            if hasattr(self.model, k):
                filters.append(getattr(self.model, k) == v)

        return filters
