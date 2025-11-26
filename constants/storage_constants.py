import os

ATTACHMENT_BUCKET = os.getenv("STORAGE_ATTACHMENT_BUCKET", "attachments")
CONTEXT_BUCKET = os.getenv("STORAGE_CONTEXT_BUCKET", "contexts")
STORAGE_PUBLIC_BASE_URL = os.getenv(
    "STORAGE_PUBLIC_BASE_URL", os.getenv("PUBLIC_API_BASE_URL", "http://localhost:8000")
).rstrip("/")

