from langdetect import detect, LangDetectException

from app.utils.arabic_utils import contains_arabic


def detect_language(text: str) -> str:
    if contains_arabic(text):
        return "ar"
    try:
        lang = detect(text)
        if lang.startswith("en"):
            return "en"
        return lang
    except LangDetectException:
        return "unknown"
