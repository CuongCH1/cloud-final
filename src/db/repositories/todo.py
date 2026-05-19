from src.db.models.todo import Todo

from .base import BaseRepository

TodoRepository = BaseRepository[Todo]
