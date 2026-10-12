import uuid
from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.models import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message
from app.services import items as items_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    items, count = items_service.list_items(
        session=session, current_user=current_user, skip=skip, limit=limit
    )
    items_public = [ItemPublic.model_validate(item) for item in items]
    return ItemsPublic(data=items_public, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    return items_service.get_item_for_user(
        session=session, current_user=current_user, item_id=id
    )


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    return items_service.create_item(
        session=session, current_user=current_user, item_in=item_in
    )


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
    return items_service.update_item(
        session=session, current_user=current_user, item_id=id, item_in=item_in
    )


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    items_service.delete_item(session=session, current_user=current_user, item_id=id)
    return Message(message="Item deleted successfully")
