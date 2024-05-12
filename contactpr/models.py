from sqlalchemy import Column, Integer, ForeignKey, String, Date, Boolean, MetaData
from pydantic import BaseModel, EmailStr
from contactpr.database import Base
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

Base = declarative_base()

metadata = MetaData()

Base.metadata = metadata


class Contact(Base):
    """
    Model for storing user contacts.

    Attributes:
        id (int): Unique identifier for the contact.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Email of the contact.
        phone_number (str): Phone number of the contact.
        birthday (Date): Birthday of the contact.
        additional_data (str, optional): Additional data about the contact (optional field).
        owner_id (int): Identifier of the owner of the contact (foreign key).
        owner (User): Relationship with the user who owns this contact.
    """
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    birthday = Column(Date)
    additional_data = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="contacts")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """
    Model for storing users.

    Attributes:
        id (int): Unique identifier for the user.
        email (str): Email of the user (unique field).
        hashed_password (str): Hashed password of the user.
        contacts (List[Contact]): List of contacts belonging to this user.
        avatar_url (str): URL of the user's avatar.
        confirmed (bool): Confirmation of user registration (default False).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    contacts = relationship("Contact", back_populates="owner")
    avatar_url = Column(String)
    confirmed = Column(Boolean, default=False)

