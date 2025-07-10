
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import os
from worker import celery
from datetime import datetime

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Holmium Technologies Pvt. Ltd.",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

@celery.task
def send_email_background(name, email, password):
    fm = FastMail(conf)

    user_html = f"""
    <p>Hi <b>{name}</b>,</p>
    <p>Below username and password are for Inventory management systme</p>
    <p><b>Your username: {name}</b>.</p>
    <p><b>Your username: {password}</b>.</p>
    <p><strong>TimeStamp:</strong><br>{datetime.now().strftime("%H:%M:%S")}</p>
    <p>Best regards,<br>Holmium Technologies Pvt. Ltd.</p>
    """

    user_message = MessageSchema(
        subject="Your account has been created for Inventory Management System!",
        recipients=[email],
        body=user_html,
        subtype=MessageType.html
    )

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fm.send_message(user_message))