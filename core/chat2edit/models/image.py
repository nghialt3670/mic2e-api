from typing import List

from PIL.Image import Image as PILImage

from core.chat2edit.models.fabric.filters import FabricFilter
from core.chat2edit.models.fabric.objects import FabricGroup, FabricImage, FabricObject
from utils.image import convert_data_url_to_image, convert_image_to_data_url


class Image(FabricGroup):
    def from_image(image: PILImage) -> "Image":
        base_image = FabricImage(
            src=convert_image_to_data_url(image), width=image.width, height=image.height
        )
        return Image(objects=[base_image])

    def set_image(self, image: PILImage) -> None:
        if not len(self.objects) == 0 or not isinstance(self.objects[0], FabricImage):
            raise ValueError("No base image found")

        self.objects[0].src = convert_image_to_data_url(image)
        self.objects[0].width = image.width
        self.objects[0].height = image.height

    def get_image(self) -> PILImage:
        if len(self.objects) == 0 or not isinstance(self.objects[0], FabricImage):
            raise ValueError("No base image found")

        if not self.objects[0].src:
            raise ValueError("No image src found")

        return convert_data_url_to_image(self.objects[0].src)

    def get_objects(self) -> List[FabricObject]:
        return self.objects[1:] if len(self.objects) > 1 else []

    def add_object(self, object: FabricObject) -> "Image":
        self.objects.append(object)
        return self

    def add_objects(self, objects: List[FabricObject]) -> "Image":
        self.objects.extend(objects)
        return self

    def remove_object(self, object: FabricObject) -> "Image":
        self.objects = [obj for obj in self.objects if obj.id != object.id]
        return self

    def remove_objects(self, objects: List[FabricObject]) -> "Image":
        object_ids = set([obj.id for obj in objects])
        self.objects = [obj for obj in self.objects if obj.id not in object_ids]
        return self

    def apply_filter(self, filter: FabricFilter) -> "Image":
        for object in self.objects:
            if isinstance(object, FabricImage):
                object.filters.append(filter)
            elif isinstance(object, Image):
                object.apply_filter(filter)

        return self
