import json
from typing import Dict

import httpx

from exception import ExternalConnectionException


class SendGridClient:
    def __init__(self, sendgrid_url: str, sendgrid_api_key: str, origin_email: str):
        self.__sendgrid_url = sendgrid_url
        self.__sendgrid_api_key = sendgrid_api_key
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
                    "value": f"This is your code: {code_recovery} to change your password"
                }
            ]
        }

    async def send_email(self, email: str, send_data: Dict):
        async with httpx.AsyncClient(**self.__headers) as client:
            response = await client.post(self.__sendgrid_url,
                                         data=json.dumps(self.__build_payload_send_email_recovery_password(
                                             addressee=email,
                                             code_recovery=send_data.get('code_recovery'))))

            if response.status_code != httpx.codes.ACCEPTED:
                raise ExternalConnectionException('Error in send email with code recovery')
