import json
from typing import Dict

import httpx

from exception import ExternalConnectionException
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendGridClient:
    def __init__(self, sendgrid_url: str, sendgrid_api_key: str, origin_email: str, link_frontend: str):
        self.__sendgrid_url = sendgrid_url
        self.__sendgrid_api_key = sendgrid_api_key
        self.__link_frontend = link_frontend
        self.__origin_email = origin_email
        self.__headers = {'headers': {'Content-Type': 'application/json',
                                      'Authorization': f'Bearer {self.__sendgrid_api_key}'}
                          }

    def __build_payload_send_email_recovery_password(self, addressee: str, code_recovery: str):
        return {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": addressee
                        }
                    ]
                }
            ],
            "from": {
                "email": self.__origin_email
            },
            "subject": "Recovery password",
            "content": [
                {
                    "type": "text/plain",
                    "value": f"This is your code: {self.__link_frontend}/recovery/password/{code_recovery} to change your password"
                }
            ]
        }

    async def send_email(self, email: str, send_data: Dict):

        
        message = MIMEMultipart()
        message["To"] = email
        message["From"] = "gustavodanieldetoledo3@gmail.com"
        message["Subject"] = "Recovery password"

        title = '<b> Title line here. </b>'
        messageText = MIMEText(f'''O codigo para recuperar sua senha é {self.__link_frontend}/recovery/password/{send_data.get('code_recovery')}.''','html')
        message.attach(messageText)

        email = 'gustavodanieldetoledo3@gmail.com'
        password = 'mzuu slqo ogvt zkjw'

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email,password)
        server.sendmail(email, message["To"], message.as_string())

        server.quit()
