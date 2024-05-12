from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from config import conf
from auth import create_email_token
from fastapi import BackgroundTasks


background_tasks = BackgroundTasks()

async def send_email(email: EmailStr, username: str, host: str):
    """
    Asynchronous function to send an email for email address confirmation.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The username to include in the email template.
        host (str): The website URL to include in the email template.

    Raises:
        Exception: Raised on failed attempts to send the email.

    Returns:
        None
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
        print("Email sent successfully.")
    except Exception as err:
        print(f"Error sending email: {err}")