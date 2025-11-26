import mimetypes

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile

from deps import get_attachment_storage_service
from schemas import AttachmentModel, ResponseModel
from services import StorageService

storage_router = APIRouter()


@storage_router.post(
    "/storage/upload",
    response_model=ResponseModel[AttachmentModel],
    summary="Upload a file to attachment storage",
)
async def upload_attachment(
    path: str = Form(..., description="Desired storage path, e.g. figs/123.fig.json"),
    file: UploadFile = File(...),
    storage_service: StorageService = Depends(get_attachment_storage_service),
) -> ResponseModel[AttachmentModel]:
    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    upload_url = await storage_service.upload(payload, path)
    return ResponseModel(
        data=AttachmentModel(
            filename=file.filename,
            upload_path=path,
            upload_url=upload_url,
        )
    )


@storage_router.get(
    "/storage/attachments/{file_path:path}",
    summary="Serve attachment content",
)
async def download_attachment(
    file_path: str,
    storage_service: StorageService = Depends(get_attachment_storage_service),
) -> Response:
    try:
        data = await storage_service.download(file_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    return Response(content=data, media_type=content_type)

