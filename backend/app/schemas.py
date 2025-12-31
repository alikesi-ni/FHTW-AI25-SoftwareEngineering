from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


ImageStatus = Literal["PENDING", "READY", "FAILED"]
DescriptionStatus = Literal["NONE", "PENDING", "READY", "FAILED"]


class PostOut(BaseModel):
    id: int
    image_filename: Optional[str] = None
    image_status: ImageStatus
    content: Optional[str] = None
    username: str
    created_at: datetime
    image_description: Optional[str] = None
    description_status: DescriptionStatus
