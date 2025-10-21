from chat2edit.context import Attachment
from chat2edit.models import ChatCycle, Message, PromptExecuteLoop

from core.chat2edit.feedbacks import ObjectExtractionQuantityMismatchFeedback

VI_EXEMPLARS = [
    ChatCycle(
        request=Message(
            text="Xóa con chó khỏi hình ảnh",
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
            text="Tôi không thể tìm thấy con chó nào trong hình ảnh. Bạn có thể cung cấp cho tôi hộp giới hạn của con chó trong hình ảnh không?"
        ),
    ),
    ChatCycle(
        request=Message(
            text="Xóa con mèo trong @box_1 và con chim trong @box_2 khỏi hình ảnh",
            attachments=[Attachment(None, basename="image")],
        ),
        loops=[
            PromptExecuteLoop(
                processed_blocks=[
                    "cat = extract_object_by_sam(image, box=box_1)",
                    "bird = extract_object_by_sam(image, box=box_2)",
                    "image_1 = remove_entities(image, [cat, bird])",
                    "respond_to_user(text='Con mèo và con chim đã được xóa khỏi hình ảnh', attachments=[image_1])",
                ],
            )
        ],
        response=Message(text="Con mèo và con chim đã được xóa khỏi hình ảnh"),
    ),
]
