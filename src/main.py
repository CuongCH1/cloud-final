import logging
from contextlib import asynccontextmanager

import aioboto3
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import SETTINGS
from src.db.models.base import BaseModel
from src.deps import get_file_upload_service, get_todo_service
from src.schemas import TodoCreate, TodoResponse
from src.services.file_upload import FileUploadService
from src.services.todo import TodoService

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    aws_session = aioboto3.Session(
        aws_access_key_id=SETTINGS.aws_access_key_id,
        aws_secret_access_key=SETTINGS.aws_secret_access_key,
        region_name=SETTINGS.region_name,
    )

    async with aws_session.resource("s3") as s3:
        app.state.s3_bucket = await s3.Bucket(SETTINGS.aws_s3_bucket_name)

        engine = create_async_engine(SETTINGS.postgres_dsn.encoded_string(), echo=True)

        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

        app.state.db_sessionmaker = async_sessionmaker(
            engine, expire_on_commit=False, autoflush=False
        )

        yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def root():
    return {"status": "ok"}


@app.post("/todos")
async def create_todo(
    form_data: TodoCreate,
    todo_service: TodoService = Depends(get_todo_service),
):
    todo = await todo_service.create(form_data.title)

    response = TodoResponse(
        id=todo.id,
        title=todo.title,
        completed=todo.completed,
    )

    return response


@app.get("/todos/{id}")
async def get_todo(
    id: str,
    todo_service: TodoService = Depends(get_todo_service),
):
    todo = await todo_service.get(id)

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    response = TodoResponse(
        id=todo.id,
        title=todo.title,
        completed=todo.completed,
    )

    return response


@app.get("/todos")
async def get_todos(
    todo_service: TodoService = Depends(get_todo_service),
):
    todos = await todo_service.get_all()

    return [TodoResponse(**todo.to_dict()) for todo in todos]


@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    file_upload_service: FileUploadService = Depends(get_file_upload_service),
):
    try:
        await file_upload_service.upload(file)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
