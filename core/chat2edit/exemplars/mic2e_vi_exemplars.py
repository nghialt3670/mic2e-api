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


def create_mic2e_vi_exemplars() -> list[Exemplar]:
    image_var = f"image_{_new_suffix()}"

    box1_var = f"box_{_new_suffix()}"
    box2_var = f"box_{_new_suffix()}"

    return [
        Exemplar(
            cycles=[
                ChatCycle(
                    request=ContextualizedMessage(
                        text="Xóa con chó khỏi ảnh",
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
thinking: Tôi cần trích xuất con chó trước khi có thể xóa nó khỏi ảnh
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
                                            text=f"""
thinking: Hàm extract_objects_by_label không thể tìm thấy con chó nào trong ảnh. Vì có hàm extract_object_by_sam, tôi có thể thử yêu cầu người dùng cung cấp khung chứa của con chó trong ảnh và sử dụng hàm extract_object_by_sam để trích xuất con chó từ ảnh
commands:
```python
respond_to_user(text='Tôi không thể tìm thấy con chó nào trong ảnh. Bạn có thể cung cấp cho tôi khung chứa của con chó trong ảnh không?')
```
""".strip(),
                                        ),
                                    ],
                                ),
                            ],
                            blocks=[
                                ExecutionBlock(
                                    is_executed=True,
                                    generated_code=f"""
respond_to_user(text='Tôi không thể tìm thấy con chó nào trong ảnh. Bạn có thể cung cấp cho tôi khung chứa của con chó trong ảnh không?')
""".strip(),
                                    processed_code=f"""
respond_to_user(text='Tôi không thể tìm thấy con chó nào trong ảnh. Bạn có thể cung cấp cho tôi khung chứa của con chó trong ảnh không?')
""".strip(),
                                    response=ContextualizedMessage(
                                        text="Tôi không thể tìm thấy con chó nào trong ảnh. Bạn có thể cung cấp cho tôi khung chứa của con chó trong ảnh không?",
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
                        text=f"Xóa con mèo trong {box1_var} và con chim trong {box2_var} khỏi ảnh",
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
thinking: vì người dùng đã cung cấp khung chứa của con mèo và con chim, tôi cần trích xuất chúng khỏi ảnh rồi sau đó xóa chúng.
commands:
```python
cat = extract_object_by_sam({image_var}, box={box1_var})
bird = extract_object_by_sam({image_var}, box={box2_var})
image_1 = remove_entities({image_var}, [cat, bird])
respond_to_user(text='Con mèo và con chim đã được xóa khỏi ảnh', paths=[image_1])
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
respond_to_user(text='Con mèo và con chim đã được xóa khỏi ảnh', paths=[image_1])
""".strip(),
                                    processed_code=f"""
cat = extract_object_by_sam({image_var}, box={box1_var})
bird = extract_object_by_sam({image_var}, box={box2_var})
image_1 = remove_entities({image_var}, [cat, bird])
respond_to_user(text='Con mèo và con chim đã được xóa khỏi ảnh', paths=[image_1])
""".strip(),
                                    response=ContextualizedMessage(
                                        text="Con mèo và con chim đã được xóa khỏi ảnh",
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


MIC2E_VI_EXEMPLARS = create_mic2e_vi_exemplars()
