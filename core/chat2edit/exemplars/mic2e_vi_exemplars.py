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

MIC2E_VI_EXEMPLARS = [
    Exemplar(
        cycles=[
            ChatCycle(
                request=ContextualizedMessage(
                    text="Xóa con chó khỏi ảnh",
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
thinking: Tôi cần trích xuất con chó trước khi có thể xóa nó khỏi ảnh
commands:
```python
dogs = extract_objects_by_label(image_0, label='dog', expected_num_objects=1)
```
""".strip(),
                                    )
                                ],
                            ),
                        ],
                        blocks=[
                            ExecutionBlock(
                                is_executed=True,
                                generated_code="""
dogs = extract_objects_by_label(image_0, label='dog', expected_num_objects=1)
""".strip(),
                                processed_code="""
dogs = extract_objects_by_label(image_0, label='dog', expected_num_objects=1)
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
                                generated_code="""
respond_to_user(text='Tôi không thể tìm thấy con chó nào trong ảnh. Bạn có thể cung cấp cho tôi khung chứa của con chó trong ảnh không?')
""".strip(),
                                processed_code="""
respond_to_user(text='Tôi không thể tìm thấy con chó nào trong ảnh. Bạn có thể cung cấp cho tôi khung chứa của con chó trong ảnh không?')
""".strip(),
                                response=ContextualizedMessage(
                                    text="Tôi không thể tìm thấy con chó nào trong ảnh. Bạn có thể cung cấp cho tôi khung chứa của con chó trong ảnh không?",
                                    paths=["image_0"],
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
                    text="Xóa con mèo trong @box_1 và con chim trong @box_2 khỏi ảnh",
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
thinking: vì người dùng đã cung cấp khung chứa của con mèo và con chim, tôi cần trích xuất chúng khỏi ảnh rồi sau đó xóa chúng.
commands:
```python
cat = extract_object_by_sam(image_0, box=box_1)
bird = extract_object_by_sam(image_0, box=box_2)
image_1 = remove_entities(image_0, [cat, bird])
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
                                generated_code="""
cat = extract_object_by_sam(image_0, box=box_1)
bird = extract_object_by_sam(image_0, box=box_2)
image_1 = remove_entities(image_0, [cat, bird])
respond_to_user(text='Con mèo và con chim đã được xóa khỏi ảnh', paths=[image_1])
""".strip(),
                                processed_code="""
cat = extract_object_by_sam(image_0, box=box_1)
bird = extract_object_by_sam(image_0, box=box_2)
image_1 = remove_entities(image_0, [cat, bird])
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
    )
]
