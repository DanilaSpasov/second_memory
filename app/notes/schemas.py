from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


NoteText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=4000,
    ),
]


class NoteCreate(BaseModel):
    text: NoteText


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: NoteText
    created_at: datetime
