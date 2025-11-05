from chat2edit.models import (
    ChatCycle,
    ContextualizedMessage,
    ExecutionBlock,
    Exemplar,
    PromptCycle,
    PromptExchange,
)
from chat2edit.models.prompt_exchange import LlmMessage

from core.chat2edit.feedbacks import LabelBasedObjectExtractionQuantityMismatchFeedback

MIC2E_EN_EXEMPLARS = [
    Exemplar(
        cycles=[
            ChatCycle(
                request=ContextualizedMessage(
                    text="Remove the dog from the image",
                    paths=["image_0"],
                ),
                cycles=[
                    PromptCycle(
                        exchanges=[
                            PromptExchange(
                                prompt=LlmMessage(text=""),
                                answers=[
                                    LlmMessage(
                                        text="""
thinking:I need to extract the dog before I can remove it from the image
commands:
```python
dogs = extract_objects_by_label(image_0, label='dog', expected_num_objects=1)
```
""",
                                    )
                                ],
                            ),
                        ],
                        blocks=[
                            ExecutionBlock(
                                is_executed=True,
                                generated_code="""
dogs = extract_objects_by_label(image_0, label='dog', expected_num_objects=1)
""",
                                processed_code="""
dogs = extract_objects_by_label(image_0, label='dog', expected_num_objects=1)
""",
                                feedback=LabelBasedObjectExtractionQuantityMismatchFeedback(
                                    severity="error",
                                    label="dog",
                                    num_expected_objects=1,
                                    num_extracted_objects=0,
                                ),
                            )
                        ],
                    ),
                    PromptCycle(
                        exchanges=[
                            PromptExchange(
                                prompt=LlmMessage(text=""),
                                answers=[
                                    LlmMessage(
                                        text="""
thinking: The extract_objects_by_label function couldn't find any dogs in the image. Since there is the extract_object_by_sam function, I could try ask the user for the bounding box of the dog in the image and use the extract_object_by_sam function to extract the dog from the image
commands:
```python
respond_to_user(text='I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?')
```
"""
                                    ),
                                ],
                            ),
                        ],
                        blocks=[
                            ExecutionBlock(
                                is_executed=True,
                                generated_code="""
respond_to_user(text='I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?')
""",
                                processed_code="""
respond_to_user(text='I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?')
""",
                                response=ContextualizedMessage(
                                    text="I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?",
                                    paths=["image_0"],
                                ),
                            )
                        ],
                    ),
                ],
            ),
            ChatCycle(
                request=ContextualizedMessage(
                    text="Remove the cat in @box_1 and the bird in @box_2 from the image",
                    paths=["image_0"],
                ),
                cycles=[
                    PromptCycle(
                        exchanges=[
                            PromptExchange(
                                prompt=LlmMessage(text=""),
                                answers=[
                                    LlmMessage(
                                        text="""
thinking: since the user provided the bounding boxes of the cat and the bird, I need to extract them from the image and then remove them.
commands:
```python
cat = extract_object_by_sam(image_0, box=box_1)
bird = extract_object_by_sam(image_0, box=box_2)
image_1 = remove_entities(image_0, [cat, bird])
respond_to_user(text='The cat and the bird have been removed from the image', paths=[image_1])
```
""",
                                    )
                                ],
                            ),
                        ],
                        blocks=[
                            ExecutionBlock(
                                is_executed=True,
                                generated_code="""
cat = extract_object_by_sam(image_0, box=box_1)
bird = extract_object_by_sam(image_0, box=box_2)
image_1 = remove_entities(image_0, [cat, bird])
respond_to_user(text='The cat and the bird have been removed from the image', paths=[image_1])
""",
                                processed_code="""
cat = extract_object_by_sam(image_0, box=box_1)
bird = extract_object_by_sam(image_0, box=box_2)
image_1 = remove_entities(image_0, [cat, bird])
respond_to_user(text='The cat and the bird have been removed from the image', paths=[image_1])
""",
                                response=ContextualizedMessage(
                                    text="The cat and the bird have been removed from the image",
                                    paths=["image_1"],
                                ),
                            )
                        ],
                    ),
                ],
            ),
        ]
    )
]
