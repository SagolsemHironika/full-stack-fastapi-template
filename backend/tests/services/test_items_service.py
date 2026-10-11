import uuid

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models import User
from app.services import items as items_service
from tests.utils.item import create_random_item
from tests.utils.user import create_random_user


def test_get_item_for_user_owner(db: Session) -> None:
    item = create_random_item(db)
    owner = db.get(User, item.owner_id)
    assert owner is not None
    result = items_service.get_item_for_user(
        session=db, current_user=owner, item_id=item.id
    )
    assert result.id == item.id


def test_get_item_for_user_not_owner(db: Session) -> None:
    item = create_random_item(db)
    other_user = create_random_user(db)
    with pytest.raises(HTTPException) as exc_info:
        items_service.get_item_for_user(
            session=db, current_user=other_user, item_id=item.id
        )
    assert exc_info.value.status_code == 403


def test_get_item_for_user_not_found(db: Session) -> None:
    user = create_random_user(db)
    with pytest.raises(HTTPException) as exc_info:
        items_service.get_item_for_user(
            session=db, current_user=user, item_id=uuid.uuid4()
        )
    assert exc_info.value.status_code == 404


def test_list_items_only_returns_own_items(db: Session) -> None:
    item = create_random_item(db)
    create_random_item(db)  # belongs to a different user
    owner = db.get(User, item.owner_id)
    assert owner is not None
    items, count = items_service.list_items(
        session=db, current_user=owner, skip=0, limit=100
    )
    assert count == 1
    assert [i.id for i in items] == [item.id]
