from typing import Union

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, UploadFile, FastAPI, Depends

from enowshop.endpoints.dependecies import verify_file_type
from enowshop.infrastructure.containers import Container

router = APIRouter()


@router.post("/uploadfile")
@inject
async def create_upload_file(file: Union[UploadFile, None] = None,
                             verify_file=Depends(verify_file_type),
                             s3_service=Depends(Provide(Container.s3_service))):
    if not file:
        return {"message": "No upload file sent"}
    else:
        url_file = s3_service.upload_file(1, file=file)
        return {"url_file": url_file}


def configure(app: FastAPI):
    app.include_router(router)