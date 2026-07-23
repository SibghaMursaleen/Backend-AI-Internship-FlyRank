from pydantic import BaseModel, Field
from typing import Optional

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, description="The title of the task")
    done: bool = Field(default=False, description="Whether the task is completed")

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="The title of the task")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, description="The title of the task")
    done: Optional[bool] = Field(default=None, description="Whether the task is completed")

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        from_attributes = True
