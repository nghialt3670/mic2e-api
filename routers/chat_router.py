from chat2edit import Chat2Edit
from chat2edit.models import Message
from fastapi import APIRouter, Depends

from utils.decorators import handle_exceptions
from deps.get_message import get_message
from deps.get_chat2edit import get_chat2edit

# Create router
router = APIRouter()


@router.post("/chat")
@handle_exceptions
async def chat_endpoint(chat2edit: Chat2Edit = Depends(get_chat2edit), message: Message = Depends(get_message), ):
    response = await chat2edit.send(message)
    chat2edit.
