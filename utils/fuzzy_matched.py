from rapidfuzz import process, fuzz


class FuzzyMatcher:
    """
    Encuentra el elemento más similar en una lista de términos normalizados.
    """

    def __init__(self, items_original: list[str], normalizer):
        self.items_original = items_original
        self.normalizer = normalizer
        self.items_normalized = [self.normalizer.normalize(item) for item in items_original]

    def find_best_match(self, user_input: str):
        user_norm = self.normalizer.normalize(user_input)

        result, score, index = process.extractOne(
            user_norm,
            self.items_normalized,
            scorer=fuzz.ratio
        )

        return {
            "original": self.items_original[index],
            "score": score
        }
