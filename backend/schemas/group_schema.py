from pydantic import Field, ConfigDict, field_validator
from typing import Optional, List, TYPE_CHECKING, Any
import datetime

from backend.schemas.util import TashkentBaseModel

if TYPE_CHECKING:
    from auth.schema import StudentRead



class GroupCreate(TashkentBaseModel):
    group_number: str = Field(..., max_length=25, description="The group number")
    mentor_id: Optional[int] = Field(
        None,
        description="id пользователя с ролью mentor (user.id); при отсутствии строки в mentor она создаётся автоматически",
    )

    @field_validator('mentor_id', mode='before')
    @classmethod
    def prevent_zero(cls, v: Any) -> Any:
        if v == 0:
            return None
        return v

    model_config = ConfigDict(extra='forbid')



class GroupUpdate(TashkentBaseModel):
    group_number: Optional[str] = Field(None, max_length=25, description="The group number")
    mentor_id: Optional[int] = Field(
        None,
        description="id пользователя с ролью mentor (user.id); при отсутствии строки в mentor она создаётся автоматически",
    )

    model_config = ConfigDict(extra='forbid')


class GroupRead(TashkentBaseModel):
    id: int = Field(..., description="The ID of the group")
    group_number: str = Field(..., description="The group number")
    mentor_id: Optional[int] = Field(None, description="The ID of the mentor")
    created_at: datetime.datetime = Field(..., description="The time the group was created")
    updated_at: datetime.datetime = Field(..., description="The time the group was updated")

    model_config = ConfigDict(from_attributes=True)

