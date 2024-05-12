from sqlalchemy.orm import Session
from contactpr import models

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user from the database by their email address.

    Args:
        db (Session): Database session object.
        email (str): Email address of the user to retrieve.

    Returns:
        User: User object if found, else None.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_data: dict):
    """
    Create a new user in the database.

    Args:
        db (Session): Database session object.
        user_data (dict): Dictionary containing user data.

    Returns:
        User: Newly created user object.
    """
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_avatar(email: str, avatar_url: str, db: Session):
    """
    Update the avatar URL of a user in the database.

    Args:
        email (str): Email address of the user whose avatar is to be updated.
        avatar_url (str): New avatar URL.
        db (Session): Database session object.

    Returns:
        User: Updated user object if user found, else None.
    """
    user = get_user_by_email(db, email)
    if user:
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        return user
    return None

async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm the email address of a user in the database.

    Args:
        email (str): Email address of the user to confirm.
        db (Session): Database session object.

    Returns:
        None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()