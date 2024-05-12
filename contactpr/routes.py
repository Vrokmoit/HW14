from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, BackgroundTasks, status, Request
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from contactpr import schemas, models, database
from contactpr.models import User
from fastapi.security import OAuth2PasswordBearer
from ..auth import create_jwt_token, get_current_user, verify_password, get_email_from_token
from fastapi_limiter.depends import RateLimiter
from .database import get_db
from ..config import settings
import cloudinary
import cloudinary.uploader
from repository import users as repository_users
from fastapi import APIRouter
from send_email import send_email
import bcrypt
from schemas import RequestEmail

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/")
async def read_root():
    """
    Root endpoint returning a welcome message.

    Returns:
        dict: Welcome message.
    """
    return {"message": "Ласкаво просимо до мого додатку FastAPI!"}

# Маршрут для створення нового контакту
@router.post("/contacts/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), 
                    rate_limiter: RateLimiter = Depends(RateLimiter(times=2, seconds=60))):
    """
    Creates a new contact in the database.

    Args:
        contact (schemas.ContactCreate): Data of the new contact.
        db (Session, optional): Database session object. Defaults to Depends(get_db).
        rate_limiter (RateLimiter, optional): Rate limiter dependency. Defaults to Depends(RateLimiter(times=2, seconds=60)).

    Returns:
        models.Contact: Created contact object.
    """
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

# Маршрут для отримання списку всіх контактів
@router.get("/contacts/", response_model=list[schemas.Contact])
def get_contacts_by_owner(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieves a list of all contacts owned by the authenticated user.

    Args:
        current_user (str): Authenticated user.
        db (Session): Database session object.

    Returns:
        List[models.Contact]: List of contacts owned by the authenticated user.
    """
    contacts = db.query(models.Contact).filter(models.Contact.owner_id == current_user.id).all()
    return contacts

# Маршрут для отримання одного контакту по його ідентифікатору
@router.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single contact by its ID.

    Args:
        contact_id (int): ID of the contact to retrieve.
        db (Session): Database session object.

    Returns:
        models.Contact: Retrieved contact object.

    Raises:
        HTTPException: If the contact with the specified ID is not found.
    """
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    return contact

# Маршрут для оновлення контакту по його ідентифікатору
@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact_update: schemas.ContactUpdate, db: Session = Depends(get_db)):
    """
    Updates a contact by its ID.

    Args:
        contact_id (int): ID of the contact to update.
        contact_update (schemas.ContactUpdate): Data to update the contact with.
        db (Session): Database session object.

    Returns:
        models.Contact: Updated contact object.

    Raises:
        HTTPException: If the contact with the specified ID is not found.
    """
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    for key, value in contact_update.dict(exclude_unset=True).items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact

# Маршрут для видалення контакту по його ідентифікатору
@router.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Deletes a contact by its ID.

    Args:
        contact_id (int): ID of the contact to delete.
        db (Session): Database session object.

    Returns:
        dict: Confirmation message upon successful deletion.

    Raises:
        HTTPException: If the contact with the specified ID is not found.
    """
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    db.delete(db_contact)
    db.commit()
    return {"message": "Контакт успішно видалено"}

# Маршрут для пошуку контактів за ім'ям, прізвищем або адресою електронної пошти
@router.get("/contacts/search/")
def search_contacts(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """
    Searches for contacts by their first name, last name, or email address.

    Args:
        query (str): Search query.
        db (Session): Database session object.

    Returns:
        List[models.Contact]: List of contacts matching the search query.
    """
    contacts = db.query(models.Contact).filter(
        models.Contact.first_name.ilike(f"%{query}%") |
        models.Contact.last_name.ilike(f"%{query}%") |
        models.Contact.email.ilike(f"%{query}%")
    ).all()
    return contacts

# Маршрут для отримання списку контактів з днями народження в найближчі 7 днів
@router.get("/contacts/birthdays/")
def upcoming_birthdays(db: Session = Depends(get_db)):
    """
    Retrieves contacts with birthdays in the next 7 days.

    Args:
        db (Session): Database session object.

    Returns:
        List[models.Contact]: List of contacts with upcoming birthdays.
    """
    today = datetime.now().date()
    week_later = today + timedelta(days=7)
    upcoming_contacts = []

    # Отримання всіх контактів з бази даних
    all_contacts = db.query(models.Contact).all()

    # Ітерація через всі контакти для перевірки, чи має кожен контакт день народження в найближчій неділі
    for contact in all_contacts:
        if contact.birthday:
            birthday_this_year = datetime(today.year, contact.birthday.month, contact.birthday.day).date()
            if today <= birthday_this_year <= week_later:
                upcoming_contacts.append(contact)

    return upcoming_contacts

# Маршрут для реєстрації користувача
@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: schemas.UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(database.get_db)):
    """
    Registers a new user.

    Args:
        body (schemas.UserCreate): Data of the new user.
        background_tasks (BackgroundTasks): Background tasks to execute.
        request (Request): Incoming HTTP request object.
        db (Session, optional): Database session object. Defaults to Depends(database.get_db).

    Returns:
        dict: User creation confirmation message.

    Raises:
        HTTPException: If the account already exists.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    hashed_password = bcrypt.hashpw(body.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = await repository_users.create_user(email=body.email, hashed_password=hashed_password, db=db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}

@router.post("/login", response_model=User)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Logs in a user.

    Args:
        body (OAuth2PasswordRequestForm): Form containing user login credentials.
        db (Session): Database session object.

    Returns:
        dict: Access token and refresh token for the authenticated user.

    Raises:
        HTTPException: If the email or password is invalid, or if the email is not confirmed.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = create_jwt_token(data={"sub": user.email})
    refresh_token = create_jwt_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms the user's email.

    Args:
        token (str): Token for email confirmation.
        db (Session): Database session object.

    Returns:
        dict: Confirmation message upon successful email confirmation.

    Raises:
        HTTPException: If the token is invalid or the user cannot be found.
    """
    email = await get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}

# Маршрут для перегляду профілю користувача
@router.get("/users/profile/", response_model=schemas.User)
async def read_user_profile(current_user: schemas.User = Depends(get_current_user)):
    """
    Retrieves the authenticated user's profile.

    Args:
        current_user (schemas.User): Authenticated user.

    Returns:
        dict: Authenticated user's profile data.
    """
    return current_user

# Маршрут для оновлення аватара користувача
@router.patch('/avatar', response_model=schemas.User)
async def update_avatar_user(file: UploadFile = File(...), 
                             current_user: models.User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """
    Updates the authenticated user's avatar.

    Args:
        file (UploadFile): Uploaded avatar file.
        current_user (models.User): Authenticated user.
        db (Session): Database session object.

    Returns:
        dict: Updated user data with the new avatar URL.
    """
    if not file:
        raise HTTPException(status_code=400, detail="Файл не був переданий")

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user

@router.post("/send-email")
async def send_email_background(email: EmailStr, background_tasks: BackgroundTasks):
    """
    Sends an email in the background.

    Args:
        email (EmailStr): Email address of the recipient.
        background_tasks (BackgroundTasks): Background tasks to execute.

    Returns:
        dict: Confirmation message upon successful email sending.
    """
    await send_email(email)
    return {"message": "email has been sent"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Requests email confirmation for a user.

    Args:
        body (RequestEmail): Email request data.
        background_tasks (BackgroundTasks): Background tasks to execute.
        request (Request): Incoming HTTP request object.
        db (Session): Database session object.

    Returns:
        dict: Confirmation message for email confirmation request.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}