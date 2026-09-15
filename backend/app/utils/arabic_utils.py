import re

ARABIC_DIACRITICS = re.compile(r"[\u0617-\u061A\u064B-\u0652]")
TATWEEL = "\u0640"

ALEF_VARIANTS = re.compile("[إأآا]")
YA_VARIANTS = re.compile("[يى]")
TA_MARBUTA = re.compile("ة")


def remove_diacritics(text: str) -> str:
    return ARABIC_DIACRITICS.sub("", text)


def normalize_arabic(text: str) -> str:
    text = text.replace(TATWEEL, "")
    text = ALEF_VARIANTS.sub("ا", text)
    text = YA_VARIANTS.sub("ي", text)
    text = TA_MARBUTA.sub("ه", text)
    return text


def contains_arabic(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text))
