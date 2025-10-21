"""
Chat route for MIC2E API using Chat2Edit
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import requests
import io
from PIL import Image as PILImage

from chat2edit import Chat2Edit, Chat2EditConfig, Chat2EditCallbacks
from chat2edit.models import Message, ChatCycle
from chat2edit.context import Attachment

from core.chat2edit.multimodal_interactive_image_editing_context_provider import MultimodalInteractiveImageEditingContextProvider
from core.chat2edit.multimodal_interactive_image_ediging_prompt_strategy import MultimodalInteractiveImageEditingPromptStrategy
from core.chat2edit.models.image import Image
from chat2edit.prompting.llms import OpenAILlm, GoogleLlm
from utils.decorators import handle_exceptions


# Create router
router = APIRouter()


def create_llm(llm_type: str, **kwargs):
    """Create LLM instance using predefined chat2edit LLMs."""
    llm_type = llm_type.lower()
    
    if llm_type == "openai":
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        llm = OpenAILlm(
            model_name=kwargs.get("model_name", "gpt-4"),
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.1)
        )
        llm.set_api_key(api_key)
        return llm
        
    elif llm_type == "google":
        api_key = kwargs.get("api_key") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        llm = GoogleLlm(
            model_name=kwargs.get("model_name", "gemini-pro"),
            max_out_tokens=kwargs.get("max_out_tokens", 2000),
            temperature=kwargs.get("temperature", 0.1)
        )
        llm.set_api_key(api_key)
        return llm
        
    else:
        raise ValueError(f"Unsupported LLM type: {llm_type}. Supported types: openai, google")


def initialize_chat2edit(language: str = "en", llm_type: str = "openai", cycles: List[ChatCycle] = None, config: Chat2EditConfig = None) -> Chat2Edit:
    """Initialize Chat2Edit instance with provided cycles and config."""
    # Create LLM instance
    llm = create_llm(llm_type)
    
    # Create context provider
    context_provider = MultimodalInteractiveImageEditingContextProvider(language)
    
    # Create prompt strategy
    strategy = MultimodalInteractiveImageEditingPromptStrategy()
    
    # Use provided config or create default
    if config is None:
        config = Chat2EditConfig(
            max_cycles_per_prompt=10,
            max_loops_per_cycle=5,
            max_prompts_per_loop=3
        )
    
    # Create callbacks
    callbacks = Chat2EditCallbacks(
        on_request=lambda msg: print(f"Request: {msg.text}"),
        on_feedback=lambda feedback: print(f"Feedback: {feedback}"),
        on_respond=lambda msg: print(f"Response: {msg.text}")
    )
    
    # Initialize Chat2Edit with provided cycles (history)
    chat2edit_instance = Chat2Edit(
        cycles=cycles or [],
        llm=llm,
        provider=context_provider,
        strategy=strategy,
        config=config,
        callbacks=callbacks
    )
    
    return chat2edit_instance


def url_to_image_object(url: str) -> Image:
    """Convert URL to Image object."""
    try:
        # Download image from URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Convert to PIL Image
        pil_image = PILImage.open(io.BytesIO(response.content))
        
        # Convert to custom Image object
        image_object = Image.from_image(pil_image)
        
        return image_object
        
    except requests.RequestException as e:
        raise ValueError(f"Failed to download image from URL {url}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to process image from URL {url}: {str(e)}")




@router.post("/chat")
@handle_exceptions
async def chat_endpoint(request_data: Dict[str, Any]):
    """Chat endpoint for multimodal image editing with attachmentUrls."""
    message = request_data.get("message", "")
    language = request_data.get("language", "en")
    llm_type = request_data.get("llm_type", "openai")
    attachment_urls = request_data.get("attachmentUrls", [])
    
    # Parse config from request
    config_data = request_data.get("config", {})
    config = Chat2EditConfig(**config_data) if config_data else None
    
    # Parse history from request
    history_data = request_data.get("history", [])
    cycles = []
    for cycle_data in history_data:
        # Convert cycle data back to ChatCycle objects
        # This is a simplified conversion - you might need more complex logic
        cycles.append(ChatCycle(**cycle_data))
    
    # Initialize Chat2Edit with config and history
    chat2edit = initialize_chat2edit(language, llm_type, cycles, config)
    
    # Process attachment URLs
    attachments = []
    for i, url in enumerate(attachment_urls):
        # Convert URL to Image object
        image_object = url_to_image_object(url)
        
        # Create attachment with Image object
        attachment = Attachment(
            data=image_object,
            basename=f"image_{i}"
        )
        attachments.append(attachment)
    
    # Create message
    user_message = Message(
        text=message,
        attachments=attachments
    )
    
    # Send message to Chat2Edit
    response = await chat2edit.send(user_message)
    
    if response:
        # Process response attachments
        response_attachments = []
        if response.attachments:
            for attachment in response.attachments:
                if attachment.data:
                    response_attachments.append({
                        "type": "image",
                        "data": attachment.data,
                        "basename": attachment.basename
                    })
        
        return JSONResponse(content={
            "success": True,
            "response": {
                "text": response.text,
                "attachments": response_attachments
            },
            "history": chat2edit.cycles  # Include updated history
        })
    else:
        return JSONResponse(content={
            "success": False,
            "error": "No response generated"
        })





