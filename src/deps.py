from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.todo import Todo
from src.db.repositories.todo import TodoRepository
from src.services.file_upload import FileUploadService
from src.services.todo import TodoService


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.db_sessionmaker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            await session.close()


def get_todo_repository(
    session: AsyncSession = Depends(get_db_session),
) -> TodoRepository:
    return TodoRepository(session, Todo)


def get_todo_service(
    repository: TodoRepository = Depends(get_todo_repository),
) -> TodoService:
    return TodoService(repository)


def get_file_upload_service(
    request: Request,
) -> FileUploadService:
    return FileUploadService(request.app.state.s3_bucket)
