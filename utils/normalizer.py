import re
import unicodedata


class TextNormalizer:
    """Responsable de normalizar texto eliminando tildes y símbolos."""

    def normalize(self, text: str) -> str:
        text = text.lower()
        text = unicodedata.normalize("NFD", text)
        text = text.encode("ascii", "ignore").decode("utf-8")
        text = re.sub(r"[^a-z0-9 ]", "", text)
        return text.strip()
