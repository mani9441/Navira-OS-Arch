class RequestParser:

    def extract_capability(
        self,
        text
    ):

        text = text.lower()

        if "weather" in text:
            return "weather"

        return None

    def extract_city(
        self,
        text
    ):

        words = text.split()

        if "in" in words:

            idx = words.index("in")

            if idx + 1 < len(words):
                return words[idx + 1]

        return "Unknown"