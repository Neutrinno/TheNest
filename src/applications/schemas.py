from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field

class StudentId(BaseModel):
    student_id: int

class ApplicationCreate(StudentId):
    first_name: str
    surname: str
    middle_name: str
    admission_score: int = Field(gt=0, lt=101)
    preferred_dormitory: Optional[Annotated[int, Field(ge=0)]] = None
    preferred_floor: Optional[Annotated[int, Field(ge=0)]] = None
    first_preferred_student: Optional[EmailStr] = None
    second_preferred_student: Optional[EmailStr] = None
    third_preferred_student: Optional[EmailStr] = None

class RoommateCreate(StudentId):
    first_preferred_student: Optional[EmailStr] = None
    second_preferred_student: Optional[EmailStr] = None
    third_preferred_student: Optional[EmailStr] = None
