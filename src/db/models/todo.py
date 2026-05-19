from typing import Any

from sqlalchemy import Boolean, String, false
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Todo(BaseModel):
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
        }
