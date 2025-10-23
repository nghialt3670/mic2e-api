import json
from typing import Any, Dict, List

from chat2edit import Chat2Edit
from chat2edit.context import Attachment
from chat2edit.models import Message
from fastapi import APIRouter, Depends

from deps import (
    get_attachment_mapping_service,
    get_attachment_file_service,
    get_chat2edit,
    get_context_file_service,
    get_message,
)
from schemas import ChatCycleModel, MessageModel, ResponseModel
from services import AttachmentMappingService, FileService
from utils.decorators import handle_exceptions
from utils.factories import create_uuid4
from utils.files import create_buffer_from_dict

router = APIRouter()


@router.post("/chat", response_model=ResponseModel[ChatCycleModel])
@handle_exceptions
async def chat_endpoint(
    message: Message = Depends(get_message),
    chat2edit: Chat2Edit = Depends(get_chat2edit),
):
    response = await chat2edit.send(message)
    cycle = chat2edit.cycles.pop()

    response = await create_message_model(response) if response else None
    context_url = await upload_context(cycle.context)

    return ResponseModel(
        data=ChatCycleModel(
            request=message,
            response=response,
            loops=cycle.loops,
            context_url=context_url,
        )
    )


async def upload_context(
    context: Dict[str, Any], context_file_service: FileService = Depends(get_context_file_service)
) -> str:
    context_bytes = json.dumps(context).encode("utf-8")
    context_path = f"{create_uuid4()}.json"
    context_url = await context_file_service.upload_file_from_bytes(
        context_bytes, context_path
    )
    return context_url


async def create_message_model(
    message: Message,
) -> MessageModel:
    attachment_urls = await upload_attachments(message.attachments)
    return MessageModel(text=message.text, attachment_urls=attachment_urls)


async def upload_attachments(
    attachments: List[Attachment],
    attachment_mapping_service: AttachmentMappingService = Depends(
        get_attachment_mapping_service
    ),
    attachment_file_service: FileService = Depends(get_attachment_file_service),
) -> List[str]:
    attachment_bytess = map(attachment_mapping_service.to_bytes, attachments)
    attachment_paths = map(f"{create_uuid4()}.json", attachment_bytess)
    attachment_urls = await attachment_file_service.upload_files_from_bytes(
        attachment_bytess, attachment_paths
    )
    return attachment_urls
