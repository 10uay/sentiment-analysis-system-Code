import re
from app.utils.arabic_utils import normalize_arabic, remove_diacritics
from app.utils.language_detector import detect_language


class TextPreprocessor:
    url_pattern = re.compile(r"https?://\S+|www\.\S+")
    mention_pattern = re.compile(r"@\w+")
    hashtag_pattern = re.compile(r"#")
    multi_space = re.compile(r"\s+")

    def clean(self, text: str) -> str:
        text = text.strip()
        text = self.url_pattern.sub(" ", text)
        text = self.mention_pattern.sub(" ", text)
        text = self.hashtag_pattern.sub("", text)
        text = remove_diacritics(text)
        text = normalize_arabic(text)
        text = self.normalize_english(text)
        text = self.multi_space.sub(" ", text).strip()
        return text

    def normalize_english(self, text: str) -> str:
        return text.replace("’", "'").replace("“", '"').replace("”", '"')

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"[\w\u0600-\u06FF']+", text.lower())

    def detect_language(self, text: str) -> str:
        return detect_language(text)
