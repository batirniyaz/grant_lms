from pydantic import ConfigDict
from backend.schemas.util import TashkentBaseModel

class StudentReadSlim(TashkentBaseModel):
    user_id: int
    student_id: int
    group_id: int = None
    is_grant: bool
    course_number: int
    attendance: int
    academic: int
    assignment: int

    model_config = ConfigDict(from_attributes=True)
