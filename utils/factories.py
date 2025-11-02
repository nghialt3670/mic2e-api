from uuid import uuid4


def create_uuid4() -> str:
    return str(uuid4())


def create_image_filename() -> str:
    return f"image_{create_uuid4()}.png"
