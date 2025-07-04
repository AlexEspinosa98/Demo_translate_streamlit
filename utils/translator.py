from .normalizer import TextNormalizer
from .fuzzy_matched import FuzzyMatcher


class Translator:
    """Orquesta la traducción con lookup directo y búsqueda aproximada."""

    def __init__(self, translation_dict: dict[str, str], min_score: int = 70):
        self.translation_dict = translation_dict
        self.normalizer = TextNormalizer()
        self.matcher = FuzzyMatcher(list(translation_dict.keys()), self.normalizer)
        self.min_score = min_score

    def translate(self, user_input: str):
        user_norm = self.normalizer.normalize(user_input)

        # Intento de match exacto
        for k, v in self.translation_dict.items():
            if self.normalizer.normalize(k) == user_norm:
                return {
                    "type": "exact",
                    "original": k,
                    "translated": v,
                    "score": 100
                }

        # Búsqueda aproximada
        fuzzy = self.matcher.find_best_match(user_input)
        fuzzy_key = fuzzy["original"]
        translated = self.translation_dict[fuzzy_key]

        if fuzzy["score"] >= self.min_score:
            return {
                "type": "fuzzy",
                "original": fuzzy_key,
                "translated": translated,
                "score": fuzzy["score"]
            }
        else:
            return {
                "type": "not_found",
                "translated": "Palabra no conocida",
                "score": fuzzy["score"],
                "original": user_input
            }
