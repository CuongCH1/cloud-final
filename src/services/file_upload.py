from uuid import uuid4

from fastapi import UploadFile


class FileUploadService:
    def __init__(self, s3_bucket):
        self.s3_bucket = s3_bucket

    async def upload(self, file: UploadFile):
        await self.s3_bucket.upload_fileobj(file.file, file.filename)
