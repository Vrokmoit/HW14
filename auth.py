from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from contactpr import models, schemas
from contactpr.database import get_db
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from config import settings
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user_data: schemas.UserCreate):
    """
    Creates a new user in the database.

    Args:
        db (Session): Database session object.
        user_data (schemas.UserCreate): Data of the new user.

    Returns:
        models.User: Created user object.
        
    Raises:
        HTTPException: If a user with the provided email already exists.
    """
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Користувач з таким email вже існує")

    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = models.User(email=user_data.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticates a user based on email and password.

    Args:
        db (Session): Database session object.
        email (str): User's email.
        password (str): User's password.

    Returns:
        models.User: Authenticated user object.

    Raises:
        HTTPException: If authentication fails.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильні облікові дані")
    return user

def create_jwt_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT token for the provided data.

    Args:
        data (dict): Data to be encoded in the token.
        expires_delta (timedelta, optional): Token expiry duration. Default is 15 minutes.

    Returns:
        str: JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str):
    """
    Verifies if the provided password matches the hashed password.

    Args:
        plain_password (str): User's input password.
        hashed_password (str): Hashed password stored in the database.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieves the current user based on the JWT token.

    Args:
        token (str): JWT token.
        db (Session): Database session object.

    Returns:
        models.User: Current user object.

    Raises:
        HTTPException: If credentials in the token cannot be validated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            raise credentials_exception
        
        return user  
    except JWTError:
        raise credentials_exception
    
def create_email_token(self, data: dict):
    """
    Creates a JWT token for email verification.

    Args:
        data (dict): Data to be encoded in the token.

    Returns:
        str: JWT token for email verification.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    return token

async def get_email_from_token(self, token: str):
    """
    Retrieves the email from a JWT token.

    Args:
        token (str): JWT token.

    Returns:
        str: Email encoded in the token.

    Raises:
        HTTPException: If the token is invalid or contains incorrect data.
    """
    try:
        payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        email = payload["sub"]
        return email
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid token for email verification")
