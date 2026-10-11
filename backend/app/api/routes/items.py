import uuid
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import ColumnElement
from sqlmodel import col, func, or_, select, text

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

router = APIRouter(prefix="/items", tags=["items"])


# Columns that clients are allowed to sort by
SORTABLE_FIELDS = {"title", "created_at"}


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    q: str | None = Query(default=None, max_length=255),
    sort_by: str = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> Any:
    """
    Retrieve items.

    - **q**: case-insensitive search on title and description
    - **sort_by**: column to sort by, or a comma-separated list, e.g.
      `title,created_at`
    - **order**: `asc` or `desc`
    """
    primary_sort = sort_by.split(",")[0].strip()
    if primary_sort not in SORTABLE_FIELDS:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot sort by '{primary_sort}'. "
            f"Allowed fields: {', '.join(sorted(SORTABLE_FIELDS))}",
        )

    filters: list[ColumnElement[bool]] = []
    if not current_user.is_superuser:
        filters = [Item.owner_id == current_user.id]

    count_statement = select(func.count()).select_from(Item).where(*filters)
    count = session.exec(count_statement).one()

    if q:
        pattern = f"%{q}%"
        filters = [
            or_(col(Item.title).ilike(pattern), col(Item.description).ilike(pattern))
        ]

    statement = (
        select(Item)
        .where(*filters)
        .order_by(text(f"{sort_by} {order}"))
        .offset(skip)
        .limit(limit)
    )
    items = session.exec(statement).all()

    items_public = [ItemPublic.model_validate(item) for item in items]
    return ItemsPublic(data=items_public, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")
