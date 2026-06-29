from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> dict:
        pass

    @abstractmethod
    def supported_formats(self) -> list[str]:
        pass
