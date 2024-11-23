import enum
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field

class StudentId(BaseModel):
    student_id: int
    class Config:
        from_attributes = True

class ApplicationCreate(StudentId):
    first_name: str
    surname: str
    middle_name: str
    admission_score: int = Field(ge=0, lt=101)
    preferred_dormitory: Optional[Annotated[int, Field(ge=0)]] = None
    preferred_floor: Optional[Annotated[int, Field(ge=0)]] = None
    first_preferred_student: Optional[EmailStr] = None
    second_preferred_student: Optional[EmailStr] = None
    third_preferred_student: Optional[EmailStr] = None


class StatusEnum(str, enum.Enum):
    Processing = "В обработке"
    Waiting = "Ожидает очереди"
    Rejected = "Отклонено"
    Approved = "Одобрено"

class Status(StudentId):
    application_id: int
    status: StatusEnum = Field(default=StatusEnum.Processing)