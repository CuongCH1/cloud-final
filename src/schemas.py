from pydantic import BaseModel


class TodoResponse(BaseModel):
    id: str
    title: str
    completed: bool


class TodoCreate(BaseModel):
    title: str
