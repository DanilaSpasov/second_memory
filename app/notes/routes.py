from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import NoteModel
from app.notes.schemas import NoteCreate, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])

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


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(note_id: NoteId, session: DbSession):
    note = await session.get(NoteModel, note_id)

    if note is not None:
        return note

    raise HTTPException(status_code=404, detail="Note not found")


@router.get("", response_model=list[NoteResponse])
async def read_notes(session: DbSession, limit: NotesLimit = 10):
    statement = select(NoteModel).order_by(NoteModel.id).limit(limit)
    notes = await session.scalars(statement)
    return notes.all()


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(note: NoteCreate, session: DbSession):
    saved_note = NoteModel(text=note.text)

    session.add(saved_note)
    await session.commit()
    await session.refresh(saved_note)

    return saved_note


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: NoteId, session: DbSession) -> None:
    note = await session.get(NoteModel, note_id)

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    await session.delete(note)
    await session.commit()
