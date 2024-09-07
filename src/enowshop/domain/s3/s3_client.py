from datetime import datetime
from io import BytesIO
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile


class S3Client:

    def __init__(self, s3_bucket_name, aws_access_key_id, aws_secret_access_key, aws_region_name):
        self.s3_bucket_name = s3_bucket_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region_name = aws_region_name
        self.client = boto3.client('s3',
                                   aws_access_key_id=self.aws_access_key_id,
                                   aws_secret_access_key=self.aws_secret_access_key)

    def upload_file(self, file: UploadFile, user_id: int) -> str:
        key = '{file_name}'.format(user_id=user_id,
                                                         extension=file.filename.split('.')[1],
                                                         file_name=file.filename)

        try:
            self.client.upload_fileobj(file.file, self.s3_bucket_name, key, ExtraArgs={'ACL': 'public-read'})
        except Exception as error:
            logging.error(error)
            raise Exception

        file_url = 'https://{bucket_name}.s3.amazonaws.com/{key}'.format(bucket_name=self.s3_bucket_name,
                                                                                  key=key,
                                                                                  region=self.aws_region_name)
        return file_url

    def upload_report(self, file: Any) -> str:
        key = '{file_name}{hash}.{extension}'.format(extension='pdf',file_name='relatorio',hash=datetime.now().strftime("%m%d%Y%H%M%S"))

        with BytesIO(file) as data:
            try:
                self.client.upload_fileobj(data, self.s3_bucket_name, key, ExtraArgs={'ACL': 'public-read'})
            except Exception as error:
                logging.error(error)
                raise Exception

            file_url = 'https://{bucket_name}.s3.amazonaws.com/{key}'.format(bucket_name=self.s3_bucket_name,
                                                                                    key=key,
                                                                                    region=self.aws_region_name)
            return file_url