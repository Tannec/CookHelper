import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def send_mail(email, subject, text):
    from_address = os.getenv("FROM")
    password = os.getenv("PASSWORD")
    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = email
    msg["Subject"] = subject
    body = text
    msg.attach(MIMEText(body, "plain"))
    server = smtplib.SMTP_SSL(os.getenv("HOST"), os.getenv("PORT"))
    server.login(from_address, password)
    server.send_message(msg)
    server.quit()
    return True


def sendVerificationMail(code=None, email=None):
    if code is None or email is None:
        return False
    subject = 'Verify your CookHelper account'
    message = "Do not reply to this mail.\n" \
              f"Verification code: {code}\n" \
              "Enter this code in CookHelper to verify your account."
    try:
        return send_mail(email, subject, message)
    except:
        return False
