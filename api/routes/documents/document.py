from typing import Dict, Optional, Union

from fastapi import APIRouter, status, File, UploadFile, Depends

from schemas.documents.documents_metadata import DocumentMetadataRead

from api.dependencies.repositories import get_repository
from core.exceptions import HTTP_400
from db.repositories.documents.documents import DocumentRepository
from db.repositories.documents.documents_metadata import DocumentMetadataRepository

router = APIRouter(tags=["Document"])


@router.post(
    "/upload",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    name="upload_document"
)
async def upload(
    file: UploadFile = File(...),
    folder: Optional[str] = None,
    repository: DocumentRepository = Depends(DocumentRepository),
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> Union[DocumentMetadataRead, Dict[str, str]]:

    if not file:
        raise HTTP_400(
            msg="No input file..."
        )

    response = await repository.upload(metadata_repo=metadata_repository, file=file, folder=folder)
    if response["response"] == "file added":
        return await metadata_repository.upload(document_upload=response["upload"])
    elif response["response"] == "file updated":
        return await metadata_repository.patch(document=response["upload"]["name"], document_patch=response["upload"])
    return response


@router.get(
    "/download",
    status_code=status.HTTP_200_OK,
    name="download_document"
)
async def download(
    file_name: str,
    repository: DocumentRepository = Depends(DocumentRepository),
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> Dict[str, str]:

    if not file_name:
        raise HTTP_400(
            msg="No file name..."
        )

    get_document_metadata = dict(await metadata_repository.get(document=file_name))

    return await repository.download(s3_url=get_document_metadata["s3_url"], name=get_document_metadata["name"])
