import re
import pandas as pd
from io import StringIO

from lingua import LanguageDetectorBuilder

detector = (
    LanguageDetectorBuilder
    .from_all_languages()
    .with_preloaded_language_models()
    .build()
)

from langdetect import detect as langdetect_detect, LangDetectException


def clean_lyrics(text: str) -> str:
    text = re.sub(r"\[.*?\]", " ", text)
    text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_language(lyrics: str) -> str:
    if not isinstance(lyrics, str) or not lyrics.strip():
        return "Unknown"

    cleaned = clean_lyrics(lyrics)

    result = detector.detect_language_of(cleaned)
    if result is not None:
        return result.name.replace("_", " ").title()

    iso_to_name = {
        "af": "Afrikaans", "sq": "Albanian", "ar": "Arabic",
        "az": "Azerbaijani", "be": "Belarusian", "bn": "Bengali",
        "bg": "Bulgarian", "ca": "Catalan", "zh-cn": "Chinese",
        "zh-tw": "Chinese (Traditional)", "hr": "Croatian",
        "cs": "Czech", "da": "Danish", "nl": "Dutch",
        "en": "English", "et": "Estonian", "fi": "Finnish",
        "fr": "French", "gl": "Galician", "ka": "Georgian",
        "de": "German", "el": "Greek", "gu": "Gujarati",
        "he": "Hebrew", "hi": "Hindi", "hu": "Hungarian",
        "is": "Icelandic", "id": "Indonesian", "it": "Italian",
        "ja": "Japanese", "kn": "Kannada", "ko": "Korean",
        "lv": "Latvian", "lt": "Lithuanian", "mk": "Macedonian",
        "ms": "Malay", "ml": "Malayalam", "mr": "Marathi",
        "ne": "Nepali", "no": "Norwegian", "fa": "Persian",
        "pl": "Polish", "pt": "Portuguese", "pa": "Punjabi",
        "ro": "Romanian", "ru": "Russian", "sk": "Slovak",
        "sl": "Slovenian", "so": "Somali", "es": "Spanish",
        "sw": "Swahili", "sv": "Swedish", "tl": "Tagalog",
        "ta": "Tamil", "te": "Telugu", "th": "Thai",
        "tr": "Turkish", "uk": "Ukrainian", "ur": "Urdu",
        "vi": "Vietnamese", "cy": "Welsh",
    }
    try:
        iso = langdetect_detect(cleaned)
        return iso_to_name.get(iso.lower(), iso.upper())
    except LangDetectException:
        return "Unknown"


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    required = {"name", "artist", "genius_id", "genius_url", "lyrics"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    result = df[["name", "artist", "genius_id", "genius_url"]].copy()
    result["language"] = df["lyrics"].apply(detect_language)
    return result

if __name__ == "__main__":
    df = pd.read_excel("songs_with_genius.xlsx")
    print("Input shape:", df.shape)

    output = process_dataframe(df)

    print("\nResult:")
    print(output.to_string(index=False))

    output.to_excel("lyrics_with_language.xlsx", index=False)
    print("\nSaved → lyrics_with_language.xlsx")