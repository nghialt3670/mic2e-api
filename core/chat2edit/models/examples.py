"""
Example usage of Fabric.js Pydantic models.
"""

from core.chat2edit.models import (
    FabricCanvas,
    FabricGroup,
    FabricImage,
    FabricRect,
    FabricText,
)


def create_canvas_example():
    """Create a simple canvas with objects."""

    # Create a rectangle
    rect = FabricRect(
        left=100, top=100, width=200, height=150, fill="rgb(255,0,0)", rx=10, ry=10
    )

    # Create text
    text = FabricText(
        left=50,
        top=300,
        text="Hello from Python!",
        fontSize=30,
        fontFamily="Arial",
        fill="rgb(0,0,255)",
    )

    # Create image
    image = FabricImage(
        left=350, top=100, width=150, height=200, src="https://picsum.photos/150/200"
    )

    # Create a group
    group = FabricGroup(
        left=50, top=400, objects=[rect.model_dump(), text.model_dump()]
    )

    # Create canvas with all objects
    canvas = FabricCanvas(
        objects=[
            rect.model_dump(),
            text.model_dump(),
            image.model_dump(),
            group.model_dump(),
        ]
    )

    return canvas


def parse_fabric_json():
    """Parse Fabric.js JSON."""

    json_data = {
        "type": "Rect",
        "left": 100,
        "top": 50,
        "width": 200,
        "height": 100,
        "fill": "rgb(0,255,0)",
    }

    rect = FabricRect(**json_data)
    print(f"Parsed rect: {rect.type} at ({rect.left}, {rect.top})")

    return rect


def modify_and_export():
    """Modify object and export to JSON."""

    text = FabricText(text="Original text")

    # Modify properties
    text.text = "Modified text"
    text.fontSize = 50
    text.fill = "rgb(255,0,0)"
    text.left = 200
    text.top = 100

    # Export to JSON
    json_output = text.model_dump_json(indent=2)
    print(json_output)

    return text


if __name__ == "__main__":
    # Example 1: Create canvas
    canvas = create_canvas_example()
    print("Canvas created with", len(canvas.objects), "objects")

    # Example 2: Parse JSON
    rect = parse_fabric_json()

    # Example 3: Modify and export
    text = modify_and_export()
