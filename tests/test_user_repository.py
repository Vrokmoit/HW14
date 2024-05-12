from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from ..repository.users import create_user, get_user_by_email, update_avatar, confirmed_email
from ..contactpr.models import User
from unittest.mock import MagicMock
import pytest


@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_create_user(db_session: Session):
    user_data = {"email": "test@example.com", "password": "password"}
    created_user = create_user(db_session, user_data)
    assert isinstance(created_user, User)
    assert created_user.email == user_data["email"]


def test_get_user_by_email(db_session: Session):
    user_data = {"email": "test@example.com", "password": "password"}
    created_user = create_user(db_session, user_data)
    retrieved_user = get_user_by_email(db_session, user_data["email"])
    assert retrieved_user == created_user


def test_update_avatar(db_session: Session):
    user_data = {"email": "test@example.com", "password": "password"}
    create_user(db_session, user_data)
    new_avatar_url = "http://example.com/avatar.jpg"
    updated_user = update_avatar(user_data["email"], new_avatar_url, db_session)
    assert updated_user.avatar_url == new_avatar_url


def test_confirmed_email(db_session: Session):
    user_data = {"email": "test@example.com", "password": "password"}
    create_user(db_session, user_data)
    confirmed_email(user_data["email"], db_session)
    user = get_user_by_email(db_session, user_data["email"])
    assert user.confirmed
