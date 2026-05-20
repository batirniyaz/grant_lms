import datetime
import pytz
from pydantic import BaseModel, field_serializer

class TashkentBaseModel(BaseModel):
    @field_serializer("*", when_used="always")
    def serialize_datetimes(self, value):
        if isinstance(value, datetime.datetime) and value.tzinfo:
            return value.astimezone(pytz.timezone("Asia/Tashkent")).isoformat()
        return value
