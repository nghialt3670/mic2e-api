from abc import ABC, abstractmethod


class Predictor(ABC):
    @abstractmethod
    def load(self, device: str) -> None:
        pass

    @abstractmethod
    def unload(self) -> None:
        pass
