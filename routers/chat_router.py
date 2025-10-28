import json
from typing import Any, Dict, List, Tuple, Type

from chat2edit import Chat2Edit
from chat2edit.context import Attachment
from chat2edit.models import Message
from fastapi import APIRouter, Depends
from chat2edit.context.utils import path_to_value
from pydantic import TypeAdapter, ValidationError

from deps import (
    get_attachment_file_service,
    get_attachment_mapping_service,
    get_chat2edit,
    get_context_file_service,
    get_message,
)
from schemas import AttachmentModel, Chat2EditRequestModel, ChatCycleModel, MessageModel, ResponseModel
from services import AttachmentMappingService, FileService
from utils.decorators import handle_exceptions
from utils.factories import create_uuid4

router = APIRouter()


@router.post("/chat", response_model=ResponseModel[ChatCycleModel])
# @handle_exceptions
async def chat_endpoint(
    request: Chat2EditRequestModel,
    message: Message = Depends(get_message),
    chat2edit: Chat2Edit = Depends(get_chat2edit),
    context_file_service: FileService = Depends(get_context_file_service),
    attachment_mapping_service: AttachmentMappingService = Depends(get_attachment_mapping_service),
    attachment_file_service: FileService = Depends(get_attachment_file_service),
):
    response = await chat2edit.send(message)
    cycle = chat2edit.cycles.pop()

    response = await create_message_model(
        response, 
        cycle.context,
        attachment_mapping_service,
        attachment_file_service
    ) if response else None
    cleaned_context = clean_context(cycle.context, Attachment)
    context_url = await upload_context(cleaned_context, context_file_service)

    return ResponseModel(
        data=ChatCycleModel(
            request=request.message,
            response=response,
            loops=cycle.loops,
            context_url=context_url,
        )
    )


async def upload_context(
    context: Dict[str, Any],
    context_file_service: FileService,
) -> str:
    context_bytes = json.dumps(context).encode("utf-8")
    context_path = f"contexts/{create_uuid4()}.context.json"
    context_url = await context_file_service.upload_file_from_bytes(
        context_bytes, context_path
    )
    return context_url


async def create_message_model(
    message: Message, 
    context: Dict[str, Any],
    attachment_mapping_service: AttachmentMappingService,
    attachment_file_service: FileService,
) -> MessageModel:
    context_paths = message.attachments
    attachments = list(map(lambda x: path_to_value(x, context), context_paths))
    attachment_paths, attachment_urls = await upload_attachments(
        attachments,
        attachment_mapping_service,
        attachment_file_service
    )
    attachment_models = []

    for i, attachment in enumerate(attachments):
        attachment_models.append(
            AttachmentModel(
                context_path=context_paths[i], 
                original_filename=attachment.__filename__ if attachment.__filename__ else create_uuid4(),
                path=attachment_paths[i], 
                url=attachment_urls[i]
            )
        )
    return MessageModel(text=message.text, attachments=attachment_models)


async def upload_attachments(
    attachments: List[Attachment],
    attachment_mapping_service: AttachmentMappingService,
    attachment_file_service: FileService,
) -> Tuple[List[str], List[str]]:
    filenames = map(lambda x: x.__filename__ if x.__filename__ else create_uuid4(), attachments)
    attachment_bytess = map(lambda x: attachment_mapping_service.to_bytes(x), attachments)
    attachment_paths = map(lambda x: f"figs/{create_uuid4()}_{x}.fig.json", filenames)
    attachment_urls = map(lambda x, y: attachment_file_service.upload_file_from_bytes(x, y), attachment_bytess, attachment_paths)
    return attachment_paths, attachment_urls


def clean_context(
    context: Dict[str, Any],
    allowed_type: Type
) -> Dict[str, Any]:
    cleaned_context = {}
    for k, v in context.items():
        try:
            TypeAdapter(allowed_type).validate_python(v)
            cleaned_context[k] = v
        except Exception as e:
            print(e)
            pass
    return cleaned_context