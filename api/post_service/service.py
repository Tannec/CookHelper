import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

HOST = 'smtp.yandex.ru'
PORT = 465
FROM = 'HestiaNet@yandex.ru'
PASSWORD = 'yljnesthciyszjmw'


def send_mail(email, subject, text):
    from_address = FROM
    password = PASSWORD
    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = email
    msg["Subject"] = subject
    body = text
    msg.attach(MIMEText(body, "plain"))
    server = smtplib.SMTP_SSL(HOST, PORT)
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
    except Exception as e:
        return str(e)
