from chat2edit.context import Attachment
from chat2edit.models import ChatCycle, Message, PromptExecuteLoop

from core.chat2edit.feedbacks import ObjectExtractionQuantityMismatchFeedback

VI_EXEMPLARS = [
    ChatCycle(
        request=Message(
            text="Remove the dog from the image",
            attachments=[Attachment(None, basename="image")],
        ),
        loops=[
            PromptExecuteLoop(
                processed_blocks=[
                    "dogs = extract_objects_by_label(image, label='dog', expected_num_objects=1)",
                ],
                feedback=ObjectExtractionQuantityMismatchFeedback(
                    severity="error",
                    num_expected_objects=1,
                    num_extracted_objects=0,
                ),
            )
        ],
        response=Message(
            text="I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?"
        ),
    ),
    ChatCycle(
        request=Message(
            text="Remove the cat in @box_1 and the bird in @box_2 from the image",
            attachments=[Attachment(None, basename="image")],
        ),
        loops=[
            PromptExecuteLoop(
                processed_blocks=[
                    "cat = extract_object_by_sam(image, box=box_1)",
                    "bird = extract_object_by_sam(image, box=box_2)",
                    "image_1 = remove_entities(image, [cat, bird])",
                    "respond_to_user(text='The cat and the bird have been removed from the image', attachments=[image_1])",
                ],
            )
        ],
        response=Message(text="The cat and the bird have been removed from the image"),
    ),
]
