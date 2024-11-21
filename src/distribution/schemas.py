from pydantic import ConfigDict, Field

class StudentList:
    model_config = ConfigDict(from_attributes=True)
    id: int
    admission_score: int = Field(gt=0, lt=101)