import uuid

from fastapi import HTTPException
from sqlmodel import Session, col, func, select

from app.models import Item, ItemCreate, ItemUpdate, User


def list_items(
    *, session: Session, current_user: User, skip: int, limit: int
) -> tuple[list[Item], int]:
    """
    Return a page of items visible to the user, and the total visible count.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = (
            select(Item).order_by(col(Item.created_at).desc()).offset(skip).limit(limit)
        )
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item)
            .where(Item.owner_id == current_user.id)
            .order_by(col(Item.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()
    return list(items), count


def get_item_for_user(
    *, session: Session, current_user: User, item_id: uuid.UUID
) -> Item:
    """
    Get an item by ID, enforcing existence and ownership (superusers bypass).
    """
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item


def create_item(*, session: Session, current_user: User, item_in: ItemCreate) -> Item:
    """
    Create an item owned by the current user.
    """
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def update_item(
    *, session: Session, current_user: User, item_id: uuid.UUID, item_in: ItemUpdate
) -> Item:
    """
    Update an item the user is allowed to modify.
    """
    item = get_item_for_user(
        session=session, current_user=current_user, item_id=item_id
    )
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_item(*, session: Session, current_user: User, item_id: uuid.UUID) -> None:
    """
    Delete an item the user is allowed to modify.
    """
    item = get_item_for_user(
        session=session, current_user=current_user, item_id=item_id
    )
    session.delete(item)
    session.commit()
