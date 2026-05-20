from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator
from typing import Optional, Any, TYPE_CHECKING, List
from pydantic import field_validator
import datetime

from auth.model import UserRole
from backend.schemas.util import TashkentBaseModel

if TYPE_CHECKING:
    from backend.schemas.group_schema import GroupRead


class Token(BaseModel):
    access_token: str = Field(..., description="The access token")
    token_type: str = Field(..., description="The token type")


class TokenData(BaseModel):
    phone: Optional[str] = Field(None, description="The phone number of the user")



class UserCreate(TashkentBaseModel):
    phone: str = Field(..., max_length=13, min_length=13, description="The phone number of the user")
    email: EmailStr = Field(..., max_length=50, description="The email of the user")
    first_name: str = Field(..., max_length=25, description="The first name of the user")
    last_name: str = Field(..., max_length=25, description="The last name of the user")
    father_name: str = Field(..., max_length=25, description="The father name of the user")
    role: UserRole = Field(..., description="The role of the user")
    password: str = Field(..., max_length=255, description="The password of the user")

    model_config = ConfigDict(extra='forbid')


class UserUpdateName(TashkentBaseModel):
    first_name: Optional[str] = Field(None, max_length=25, description="The first name of the user")
    last_name: Optional[str] = Field(None, max_length=25, description="The last name of the user")
    father_name: Optional[str] = Field(None, max_length=25, description="The father name of the user")

    model_config = ConfigDict(extra='forbid')


class UserUpdateUnique(TashkentBaseModel):
    phone: Optional[str] = Field(None, max_length=13, min_length=13, description="The phone number of the user")
    email: Optional[EmailStr] = Field(None, max_length=50, description="The email of the user")

    model_config = ConfigDict(extra='forbid')


class UserUpdatePassword(TashkentBaseModel):
    password: str = Field(..., max_length=255, description="The password of the user")

    model_config = ConfigDict(extra='forbid')


class UserRead(TashkentBaseModel):
    id: int = Field(..., description="The ID of the user")
    phone: str = Field(..., description="The phone number of the user")
    email: EmailStr = Field(..., description="The email of the user")
    first_name: str = Field(..., description="The first name of the user")
    last_name: str = Field(..., description="The last name of the user")
    father_name: str = Field(..., description="The father name of the user")
    role: UserRole = Field(..., description="The role of the user")
    created_at: datetime.datetime = Field(..., description="The time the user was created")
    updated_at: datetime.datetime = Field(..., description="The time the user was updated")

    model_config = ConfigDict(from_attributes=True)



class AdminCreate(UserCreate):
    role: UserRole = Field(..., description="The role of the user")
    is_superadmin: bool = Field(..., description="The superuser status of the admin")

    model_config = ConfigDict(extra='forbid')


class AdminRead(UserRead):
    user_id: int = Field(..., description="The ID of the user associated with this admin")
    is_superadmin: bool = Field(..., description="The superuser status of the admin")
    created_at: datetime.datetime = Field(..., description="The time the admin was created")
    updated_at: datetime.datetime = Field(..., description="The time the admin was updated")

    @model_validator(mode='before')
    @classmethod
    def flatten_user(cls, data: Any) -> Any:
        # Use user_id as the main 'id' for the Read schema
        if hasattr(data, 'user_id'):
            setattr(data, 'id', data.user_id)
        if hasattr(data, 'user') and data.user:
            for field in ['phone', 'email', 'first_name', 'last_name', 'father_name', 'role']:
                setattr(data, field, getattr(data.user, field))
        return data

    model_config = ConfigDict(from_attributes=True)


class StudentCreate(UserCreate):
    # student-specific
    student_id: int = Field(..., description="The student ID (business ID)")
    group_id: Optional[int] = Field(None, description="The ID of the group")
    is_grant: bool = Field(default=False, description="Whether the student is on a grant")
    course_number: int = Field(default=1, description="The course number")
    attendance: int = Field(default=0, description="Attendance score")
    academic: int = Field(default=0, description="Academic score")
    assignment: int = Field(default=0, description="Assignment score")

    @field_validator('group_id', mode='before')
    @classmethod
    def prevent_zero(cls, v: Any) -> Any:
        if v == 0:
            return None
        return v

    model_config = ConfigDict(extra='forbid')



class StudentRead(UserRead):
    user_id: int = Field(..., description="The ID of the user associated with this student")
    student_id: int = Field(..., description="The student ID (business ID)")
    group_id: Optional[int] = Field(..., description="The ID of the group")
    is_grant: bool = Field(..., description="Whether the student is on a grant")
    course_number: int = Field(..., description="The course number")
    attendance: int = Field(default=0, description="Attendance score")
    academic: int = Field(default=0, description="Academic score")
    assignment: int = Field(default=0, description="Assignment score")
    created_at: datetime.datetime = Field(..., description="The time the student was created")
    updated_at: datetime.datetime = Field(..., description="The time the student was updated")

    monthly_scores: List["MonthlyScoreRead"] = Field(default_factory=list)
    certificates: List["CertificateRead"] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def flatten_user(cls, data: Any) -> Any:
        if hasattr(data, 'user_id'):
            setattr(data, 'id', data.user_id)
        if hasattr(data, 'user') and data.user:
            for field in ['phone', 'email', 'first_name', 'last_name', 'father_name', 'role']:
                setattr(data, field, getattr(data.user, field))
        return data

    model_config = ConfigDict(from_attributes=True)


class MonthlyScoreCreate(TashkentBaseModel):
    student_id: int
    month: int
    year: int
    academic_percent: Optional[float] = 0.0
    attendance_percent: Optional[float] = 0.0
    assignment_score: Optional[float] = 0.0
    discipline_score: Optional[float] = 0.0
    tutor_score: Optional[float] = 0.0
    penalty_score: Optional[float] = 0.0
    recovery_score: Optional[float] = 0.0
    employment_score: Optional[float] = 0.0

    model_config = ConfigDict(extra='forbid')


class MonthlyScoreRead(MonthlyScoreCreate):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class MonthlyScoreUpdate(TashkentBaseModel):
    academic_percent: Optional[float] = None
    attendance_percent: Optional[float] = None
    assignment_score: Optional[float] = None
    discipline_score: Optional[float] = None
    tutor_score: Optional[float] = None
    penalty_score: Optional[float] = None
    recovery_score: Optional[float] = None
    employment_score: Optional[float] = None

    model_config = ConfigDict(extra='forbid')


class CertificateCreate(TashkentBaseModel):
    title: str = Field(..., max_length=100)
    cert_type: str = Field(..., description="Type of certificate from predefined list")

class CertificateRead(TashkentBaseModel):
    id: int
    student_id: int
    title: str
    cert_type: str
    file_path: str
    status: str
    points: float
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class CertificateUpdateStatus(TashkentBaseModel):
    status: str # 'approved' or 'rejected'

    model_config = ConfigDict(extra='forbid')


class LeaderboardRow(TashkentBaseModel):
    student_name: str
    group_name: Optional[str]
    student_id: int
    current_status: str # "Grant" or "Kontrakt"

    academic_percent: float
    academic_ball: float
    attendance_percent: float
    attendance_ball: float
    assignment_ball: float
    activity_ball: float
    tutor_ball: float
    discipline_ball: float

    total_kpi: float
    penalty: float
    recovery: float
    employment: float

    final_score: float
    next_status: str
    risk: str



class StudentUpdate(TashkentBaseModel):

    group_id: Optional[int] = Field(None)
    is_grant: Optional[bool] = Field(None)
    course_number: Optional[int] = Field(None)
    attendance: Optional[int] = Field(None)
    academic: Optional[int] = Field(None)
    assignment: Optional[int] = Field(None)

    model_config = ConfigDict(extra='forbid')



class MentorCreate(UserCreate):

    group_ids: list[int] = Field(default_factory=list, description="Optional list of group IDs to assign to mentor")

    model_config = ConfigDict(extra='forbid')


class MentorRead(UserRead):
    user_id: int = Field(..., description="The ID of the user associated with this mentor")

    groups: List["GroupRead"] = Field(default_factory=list, description="Groups assigned to mentor")
    created_at: datetime.datetime = Field(..., description="The time the mentor was created")
    updated_at: datetime.datetime = Field(..., description="The time the mentor was updated")

    @model_validator(mode='before')
    @classmethod
    def flatten_user(cls, data: Any) -> Any:
        if hasattr(data, 'user_id'):
            setattr(data, 'id', data.user_id)
        if hasattr(data, 'user') and data.user:
            for field in ['phone', 'email', 'first_name', 'last_name', 'father_name', 'role']:
                setattr(data, field, getattr(data.user, field))
        return data

    model_config = ConfigDict(from_attributes=True)


class MentorUpdate(TashkentBaseModel):

    group_ids: Optional[list[int]] = Field(None)

    model_config = ConfigDict(extra='forbid')

