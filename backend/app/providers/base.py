from abc import ABC, abstractmethod
from pathlib import Path


class TryOnProvider(ABC):
    name: str

    @abstractmethod
    def generate(
        self,
        person_image_path: Path,
        garment_image_url: str,
        category: str,
    ) -> bytes:
        """Generate a try-on image. Returns the result image as bytes (JPEG)."""
        ...
