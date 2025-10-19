from typing import List

from PIL.Image import Image as PILImage

from core.chat2edit.models.fabric.objects import FabricGroup, FabricImage, FabricObject


class Image(FabricGroup):
    def from_image(image: PILImage) -> "Image":
        base_image = FabricImage(
            src=image.tobytes().decode("utf-8"), width=image.width, height=image.height
        )
        return Image(objects=[base_image])

    def set_image(self, image: PILImage) -> None:
        if not len(self.objects) == 0 or not isinstance(self.objects[0], FabricImage):
            raise ValueError("No base image found")

        self.objects[0].src = image.tobytes().decode("utf-8")
        self.objects[0].width = image.width
        self.objects[0].height = image.height

    def get_image(self) -> PILImage:
        if not len(self.objects) == 0 or not isinstance(self.objects[0], FabricImage):
            raise ValueError("No base image found")

        if not self.objects[0].src:
            raise ValueError("No image src found")

        return PILImage.frombytes(self.objects[0].src)

    def remove_object(self, object: FabricObject) -> "Image":
        self.objects = [obj for obj in self.objects if obj.id != object.id]
        return self

    def remove_objects(self, objects: List[FabricObject]) -> "Image":
        object_ids = set([obj.id for obj in objects])
        self.objects = [obj for obj in self.objects if obj.id not in object_ids]
        return self
