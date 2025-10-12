from chat2edit.prompting.strategies import OtcStrategy


class InteractivePromptStrategy(OtcStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_prompt(self, image: Image.Image, prompt: str) -> str:
        return super().generate_prompt(image, prompt)
