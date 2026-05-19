from src.db.models.todo import Todo
from src.db.repositories.todo import TodoRepository


class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    async def create(self, title: str) -> Todo:
        todo = Todo(title=title)
        todo = await self.repository.create(todo)

        return todo

    async def get(self, id: str) -> Todo | None:
        todo = await self.repository.get(id)

        return todo

    async def get_all(self) -> list[Todo]:
        todos = await self.repository.find()

        return todos
