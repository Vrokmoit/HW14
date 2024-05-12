from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class ContactBase(BaseModel):
    """
    Base schema for contact data.

    Attributes:
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Email address of the contact.
        phone_number (str): Phone number of the contact.
        birthday (Optional[datetime.date], optional): Birthday of the contact (optional).
        additional_data (Optional[str], optional): Additional data about the contact (optional).
    """
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: Optional[datetime.date] = None
    additional_data: Optional[str] = None

class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.

    Inherits attributes from ContactBase.
    """
    pass

class Contact(ContactBase):
    """
    Schema for representing a contact.

    Inherits attributes from ContactBase and adds an 'id' attribute.

    Attributes:
        id (int): Unique identifier for the contact.
    """
    id: int

    class Config:
        orm_mode = True

class ContactUpdate(BaseModel):
    """
    Schema for updating an existing contact.

    Attributes:
        first_name (Optional[str], optional): Updated first name of the contact (optional).
        last_name (Optional[str], optional): Updated last name of the contact (optional).
        email (Optional[str], optional): Updated email address of the contact (optional).
        phone_number (Optional[str], optional): Updated phone number of the contact (optional).
        birthday (Optional[datetime.date], optional): Updated birthday of the contact (optional).
        additional_data (Optional[str], optional): Updated additional data about the contact (optional).
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birthday: Optional[datetime.date] = None
    additional_data: Optional[str] = None

class UserBase(BaseModel):
    """
    Base schema for user data.

    Attributes:
        email (str): Email address of the user.
        avatar_url (Optional[str], optional): URL of the user's avatar (optional).
    """
    email: str
    avatar_url: Optional[str]

class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Inherits attributes from UserBase and adds a 'password' attribute.

    Attributes:
        password (str): Password of the user.
    """
    password: str

class User(UserBase):
    """
    Schema for representing a user.

    Inherits attributes from UserBase and adds an 'id' attribute.

    Attributes:
        id (int): Unique identifier for the user.
    """
    id: int

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """
    Schema for user login data.

    Attributes:
        email (str): Email address of the user.
        password (str): Password of the user.
    """
    email: str
    password: str

class EmailSchema(BaseModel):
    """
    Schema for representing an email address.

    Attributes:
        email (EmailStr): Email address.
    """
    email: EmailStr

class RequestEmail(BaseModel):
    """
    Schema for requesting an email address.

    Attributes:
        email (EmailStr): Email address.
    """
    email: EmailStr