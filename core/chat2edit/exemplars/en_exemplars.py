from chat2edit.context import Attachment
from chat2edit.models import ChatCycle, Message, PromptExecuteLoop

VI_EXEMPLARS = [
    ChatCycle(
        request=Message(
            text="Remove the dog from the image",
            attachments=[Attachment(None, basename="image")],
        ),
        loops=[
            PromptExecuteLoop(
                prompts=[""],
                answers=[
                    """
                ```python
                dogs = extract_objects_by_label(image, "dog", expected_num_objects=1)
                image = remove_entities(image, dogs)
                ```
                """
                ],
            )
        ],
        response=Message(text="The red object has been removed from the image"),
    )
]
