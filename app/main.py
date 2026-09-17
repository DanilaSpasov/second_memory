from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict, StringConstraints
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import NoteModel

NoteText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=4000,
    ),
]

NoteId = Annotated[
    int,
    Path(
        gt=0,
        description="Идентификатор заметки",
    ),
]

NotesLimit = Annotated[
    int,
    Query(
        ge=1,
        le=100,
        description="Максимальное количество заметок",
    ),
]

DbSession = Annotated[AsyncSession, Depends(get_db)]


class NoteCreate(BaseModel):
    text: NoteText


class Note(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: NoteText
    created_at: datetime


app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes/{note_id}", response_model=Note)
async def read_note(note_id: NoteId, session: DbSession):
    note = await session.get(NoteModel, note_id)

    if note is not None:
        return note

    raise HTTPException(status_code=404, detail="Note not found")


@app.get("/notes", response_model=list[Note])
async def read_notes(session: DbSession, limit: NotesLimit = 10):
    statement = select(NoteModel).order_by(NoteModel.id).limit(limit)
    notes = await session.scalars(statement)
    return list(notes)


@app.post("/notes", response_model=Note, status_code=201)
async def create_note(note: NoteCreate, session: DbSession):
    saved_note = NoteModel(
        text=note.text,
    )

    session.add(saved_note)
    await session.commit()
    await session.refresh(saved_note)

    return saved_note
