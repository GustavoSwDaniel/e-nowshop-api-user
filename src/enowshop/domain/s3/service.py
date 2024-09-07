from datetime import datetime
from typing import Any

from fastapi import UploadFile

from enowshop.domain.s3.s3_client import S3Client


class S3Service:
    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client

    @staticmethod
    def _create_file_name(file: UploadFile) -> str:
        file_name = '{date}.{content_type}'.format(date=datetime.now().strftime("%m%d%Y%H%M%S"),
                                                   content_type=file.filename.split('.')[1])
        return file_name

    def upload_file(self, user_id: int, file: Any) -> str:
        file.filename = self._create_file_name(file)
        url = self.s3_client.upload_file(file, user_id)
        return url
    
    def upload_report(self, file: Any) -> str:
        url = self.s3_client.upload_report(file)
        return url
