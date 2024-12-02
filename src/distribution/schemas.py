from pydantic import ConfigDict, Field, BaseModel

class StudentList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    admission_score: int = Field(ge=0, lt=101)

class StudentStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    application_id: int
    student_id: int
    status: str