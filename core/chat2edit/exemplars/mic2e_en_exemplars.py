from chat2edit.models import (
    ChatCycle,
    ContextualizedMessage,
    ExecutionBlock,
    Exemplar,
    PromptCycle,
    PromptExchange,
)
from chat2edit.models.prompt_exchange import LlmMessage

from uuid import uuid4

from core.chat2edit.feedbacks import LabelBasedObjectExtractionQuantityMismatchFeedback


def _new_suffix() -> str:
    return str(uuid4()).split("-")[0]


def create_mic2e_en_exemplars() -> list[Exemplar]:
    """
    Build exemplars with dynamically constructed variable names such as:
    - image_<id_prefix> instead of hard-coded image_0
    - box_<id_prefix> for bounding boxes
    """
    image_var = f"image_{_new_suffix()}"

    box1_var = f"box_{_new_suffix()}"
    box2_var = f"box_{_new_suffix()}"

    return [
        Exemplar(
            cycles=[
                ChatCycle(
                    request=ContextualizedMessage(
                        text="Remove the dog from the image",
                        paths=[image_var],
                    ),
                    cycles=[
                        PromptCycle(
                            exchanges=[
                                PromptExchange(
                                    prompt=LlmMessage(text=""),
                                    answers=[
                                        LlmMessage(
                                            text=f"""
thinking:I need to extract the dog before I can remove it from the image
commands:
```python
dogs = extract_objects_by_label({image_var}, label='dog', expected_num_objects=1)
```
""".strip(),
                                        )
                                    ],
                                ),
                            ],
                            blocks=[
                                ExecutionBlock(
                                    is_executed=True,
                                    generated_code=f"""
dogs = extract_objects_by_label({image_var}, label='dog', expected_num_objects=1)
""".strip(),
                                    processed_code=f"""
dogs = extract_objects_by_label({image_var}, label='dog', expected_num_objects=1)
""".strip(),
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
""".strip(),
                                        ),
                                    ],
                                ),
                            ],
                            blocks=[
                                ExecutionBlock(
                                    is_executed=True,
                                    generated_code="""
respond_to_user(text='I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?')
""".strip(),
                                    processed_code="""
respond_to_user(text='I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?')
""".strip(),
                                    response=ContextualizedMessage(
                                        text="I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?",
                                        paths=[image_var],
                                    ),
                                )
                            ],
                        ),
                    ],
                ),
            ]
        ),
        Exemplar(
            cycles=[
                ChatCycle(
                    request=ContextualizedMessage(
                        text=f"Remove the cat in {box1_var} and the bird in {box2_var} from the image",
                        paths=[image_var],
                    ),
                    cycles=[
                        PromptCycle(
                            exchanges=[
                                PromptExchange(
                                    prompt=LlmMessage(text=""),
                                    answers=[
                                        LlmMessage(
                                            text=f"""
thinking: since the user provided the bounding boxes of the cat and the bird, I need to extract them from the image and then remove them.
commands:
```python
cat = extract_object_by_sam({image_var}, box={box1_var})
bird = extract_object_by_sam({image_var}, box={box2_var})
image_1 = remove_entities({image_var}, [cat, bird])
respond_to_user(text='The cat and the bird have been removed from the image', attachments=[image_1])
```
""".strip(),
                                        )
                                    ],
                                ),
                            ],
                            blocks=[
                                ExecutionBlock(
                                    is_executed=True,
                                    generated_code=f"""
cat = extract_object_by_sam({image_var}, box={box1_var})
bird = extract_object_by_sam({image_var}, box={box2_var})
image_1 = remove_entities({image_var}, [cat, bird])
respond_to_user(text='The cat and the bird have been removed from the image', attachments=[image_1])
""".strip(),
                                    processed_code=f"""
cat = extract_object_by_sam({image_var}, box={box1_var})
bird = extract_object_by_sam({image_var}, box={box2_var})
image_1 = remove_entities({image_var}, [cat, bird])
respond_to_user(text='The cat and the bird have been removed from the image', attachments=[image_1])
""".strip(),
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
        ),
    ]


# Keep original constant for existing imports
MIC2E_EN_EXEMPLARS = create_mic2e_en_exemplars()
