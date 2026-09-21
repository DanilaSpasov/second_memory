from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import NoteModel, OwnerModel
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
TelegramUserId = Annotated[
    int,
    Header(
        alias="X-Telegram-User-Id",
        gt=0,
        description="Telegram ID владельца для локального API",
    ),
]


async def get_current_owner(
    telegram_user_id: TelegramUserId,
    session: DbSession,
) -> OwnerModel:
    statement = select(OwnerModel).where(
        OwnerModel.telegram_user_id == telegram_user_id
    )
    owner = await session.scalar(statement)

    if owner is None:
        owner = OwnerModel(telegram_user_id=telegram_user_id)
        session.add(owner)
        await session.commit()
        await session.refresh(owner)

    return owner


CurrentOwner = Annotated[OwnerModel, Depends(get_current_owner)]


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(
    note_id: NoteId,
    session: DbSession,
    owner: CurrentOwner,
):
    statement = select(NoteModel).where(
        NoteModel.id == note_id,
        NoteModel.owner_id == owner.id,
    )
    note = await session.scalar(statement)

    if note is not None:
        return note

    raise HTTPException(status_code=404, detail="Note not found")


@router.get("", response_model=list[NoteResponse])
async def read_notes(
    session: DbSession,
    owner: CurrentOwner,
    limit: NotesLimit = 10,
):
    statement = (
        select(NoteModel)
        .where(NoteModel.owner_id == owner.id)
        .order_by(NoteModel.id)
        .limit(limit)
    )
    notes = await session.scalars(statement)
    return notes.all()


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(
    note: NoteCreate,
    session: DbSession,
    owner: CurrentOwner,
):
    saved_note = NoteModel(
        owner_id=owner.id,
        text=note.text,
    )

    session.add(saved_note)
    await session.commit()
    await session.refresh(saved_note)

    return saved_note


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: NoteId,
    session: DbSession,
    owner: CurrentOwner,
) -> None:
    statement = select(NoteModel).where(
        NoteModel.id == note_id,
        NoteModel.owner_id == owner.id,
    )
    note = await session.scalar(statement)

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    await session.delete(note)
    await session.commit()
