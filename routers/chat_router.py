from chat2edit import Chat2Edit
from chat2edit.models import ChatMessage
from fastapi import APIRouter, Depends

from deps import (
    get_attachment_serialization_service,
    get_attachment_storage_service,
    get_chat2edit,
    get_context_serialization_service,
    get_context_storage_service,
)
from schemas import (
    AttachmentModel,
    ChatRequestModel,
    ChatResponseModel,
    MessageModel,
    ResponseModel,
)
from services import (
    AttachmentSerializationService,
    ContextSerializationService,
    StorageService,
)
from utils.factories import create_uuid4

chat_router = APIRouter()


@chat_router.post("/chat", response_model=ResponseModel[ChatResponseModel])
async def chat(
    request: ChatRequestModel,
    chat2edit: Chat2Edit = Depends(get_chat2edit),
    context_storage_service: StorageService = Depends(get_context_storage_service),
    context_serialization_service: ContextSerializationService = Depends(
        get_context_serialization_service
    ),
    attachment_storage_service: StorageService = Depends(
        get_attachment_storage_service
    ),
    attachment_serialization_service: AttachmentSerializationService = Depends(
        get_attachment_serialization_service
    ),
):
    request_message = ChatMessage(text=request.message.text)
    for attachment in request.message.attachments:
        attachment_bytes = await attachment_storage_service.download(
            attachment.upload_url
        )
        attachment = attachment_serialization_service.deserialize(attachment_bytes)
        request_message.attachments.append(attachment)

    context = {}
    if request.context_url:
        context_bytes = await context_storage_service.download(request.context_url)
        context = context_serialization_service.deserialize(context_bytes)

    response_message, cycle, updated_context = await chat2edit.generate(
        request_message, request.history, context
    )

    context_bytes = context_serialization_service.serialize(updated_context)
    context_path = f"contexts/{create_uuid4()}.context.json"
    context_url = await context_storage_service.upload(context_bytes, context_path)

    if not response_message:
        return (
            ResponseModel(
                data=ChatResponseModel(
                    cycle=cycle,
                    context_url=context_url,
                )
            ),
        )

    response_message_model = MessageModel(
        text=response_message.text,
    )
    for attachment in response_message.attachments:
        attachment_bytes = attachment_serialization_service.serialize(attachment)
        attachment_filename = f"{create_uuid4()}.fig.json"
        attachment_path = f"figs/{attachment_filename}"
        attachment_url = await attachment_storage_service.upload(
            attachment_bytes, attachment_path
        )
        response_message_model.attachments.append(
            AttachmentModel(
                filename=attachment_filename,
                upload_path=attachment_path,
                upload_url=attachment_url,
            )
        )

    return ResponseModel(
        data=ChatResponseModel(
            message=response_message_model,
            cycle=cycle,
            context_url=context_url,
        )
    )
