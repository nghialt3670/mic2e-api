# MIC2E API - Multimodal Interactive Image Editing

A FastAPI-based API for multimodal interactive image editing using Chat2Edit framework.

## Features

- **Multimodal Image Editing**: Process images with natural language instructions
- **Multiple LLM Support**: OpenAI GPT-4 and Google Gemini Pro
- **Bilingual Support**: English and Vietnamese language support
- **RESTful API**: Easy-to-use HTTP endpoints
- **Image URL Support**: Process images via attachment URLs with automatic Image object creation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):
```bash
export OPENAI_API_KEY="your_openai_api_key"
export GOOGLE_API_KEY="your_google_api_key"
```

## Running the API

### Option 1: Using the startup script
```bash
python run.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using Python directly
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Health Check
- **GET** `/` - Root endpoint
- **GET** `/health` - Health check with predictor manager status

### 2. Chat Endpoint

#### POST `/api/v1/chat`
JSON endpoint for image editing with attachment URLs.

**Request Body:**
```json
{
  "message": "Remove the dog from the image",
  "language": "en",
  "llm_type": "openai",
  "attachmentUrls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.png"
  ],
  "config": {
    "max_cycles_per_prompt": 10,
    "max_loops_per_cycle": 5,
    "max_prompts_per_loop": 3
  },
  "history": []
}
```

**Parameters:**
- `message` (string, required): User's text instruction
- `language` (string, optional): Language preference ("en" or "vi", default: "en")
- `llm_type` (string, optional): LLM type ("openai", "google", default: "openai")
- `attachmentUrls` (array, optional): List of image URLs to process (automatically converted to Image objects)
- `config` (object, optional): Chat2Edit configuration parameters
- `history` (array, optional): Previous conversation history (ChatCycle objects)

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Remove the dog from the image",
    "language": "en",
    "llm_type": "openai",
    "attachmentUrls": ["https://example.com/image.jpg"],
    "config": {
      "max_cycles_per_prompt": 10,
      "max_loops_per_cycle": 5,
      "max_prompts_per_loop": 3
    },
    "history": []
  }'
```

## Response Format

All chat endpoints return responses in the following format:

```json
{
  "success": true,
  "response": {
    "text": "The dog has been removed from the image",
    "attachments": [
      {
        "type": "image",
        "data": "base64_encoded_result_image",
        "basename": "result_image"
      }
    ]
  },
  "history": [
    // Updated conversation history with new ChatCycle
  ]
}
```

## Supported Operations

The API supports various image editing operations through natural language:

- **Object Removal**: "Remove the dog from the image"
- **Object Extraction**: "Extract the cat from the image"
- **Object Detection**: "Find all cars in the image"
- **Image Filtering**: "Apply brightness filter to the image"
- **Multi-object Operations**: "Remove the cat and bird from the image"

## LLM Configuration

### OpenAI GPT-4 (Default)
- Requires `OPENAI_API_KEY` environment variable
- Set `llm_type` to "openai"
- High-quality responses for production use

### Google Gemini Pro
- Requires `GOOGLE_API_KEY` environment variable
- Set `llm_type` to "google"
- Alternative high-quality LLM option

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid request parameters
- **500 Internal Server Error**: Server-side errors with detailed messages

Error responses include:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Development

### Project Structure
```
mic2e-api/
├── main.py                          # FastAPI application
├── run.py                           # Startup script
├── requirements.txt                 # Dependencies
├── routes/
│   └── chat_route.py               # Chat endpoints
├── core/
│   ├── chat2edit/                 # Chat2Edit components
│   └── inference/                  # Inference management
└── config/                         # Model configurations
```

### Adding New Features

1. **New Chat Functions**: Add to `core/chat2edit/functions/`
2. **New Feedback Types**: Add to `core/chat2edit/feedbacks/`
3. **New Endpoints**: Add to `routers/` directory

### Exception Handling Decorators

The API includes decorators for automatic exception handling:

#### `@handle_exceptions`
Automatically catches exceptions and converts them to appropriate HTTP status codes:
- `ValueError` → 400 Bad Request
- `PermissionError` → 403 Forbidden  
- `FileNotFoundError` → 404 Not Found
- Other exceptions → 500 Internal Server Error

```python
from utils.decorators import handle_exceptions

@router.post("/my-endpoint")
@handle_exceptions
async def my_endpoint():
    # No need for try-catch blocks
    # Exceptions are automatically handled
    return {"message": "Success"}
```

#### `@handle_exceptions_with_status(status_code)`
Handle exceptions with a specific HTTP status code:

```python
from utils.decorators import handle_exceptions_with_status

@router.get("/custom-error")
@handle_exceptions_with_status(418)
async def custom_error():
    raise Exception("This will return 418 status")
```

#### `@validate_required_params(*params)`
Validate that required parameters are present:

```python
from utils.decorators import validate_required_params

@router.post("/validate")
@handle_exceptions
@validate_required_params("name", "email")
async def validate_endpoint(name: str, email: str):
    return {"name": name, "email": email}
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **LLM API Errors**: Check API keys and network connectivity
3. **Image Processing Errors**: Ensure images are in supported formats (PNG, JPEG)

### Logs

The application logs important events:
- Request processing
- LLM interactions
- Error details
- Predictor manager status

Check console output for detailed logging information.
