"""
fetch_lyrics.py
───────────────
Парсит тексты песен через внутренний Musixmatch API
(apic-desktop.musixmatch.com) — аналог PHP-кода из репозитория.

Запуск:
    pip install requests openpyxl pandas
    python fetch_lyrics.py

Файл 234.xlsx должен лежать рядом со скриптом.
Прогресс сохраняется в 234_with_lyrics.xlsx после каждой песни.
"""

import json
import os
import re
import time
import pandas as pd
import requests

# ── константы API (из PHP-кода) ───────────────────────────────────────────────
APP_ID        = "web-desktop-app-v1.0"
BASE          = "https://apic-desktop.musixmatch.com/ws/1.1"
TOKEN_URL     = f"{BASE}/token.get?app_id={APP_ID}"
SEARCH_URL    = f"{BASE}/macro.search?app_id={APP_ID}&page_size=5&page=1&s_track_rating=desc&quorum_factor=1.0"
LYRICS_URL    = f"{BASE}/track.subtitle.get?app_id={APP_ID}&subtitle_format=lrc"
LYRICS_ALT    = f"{BASE}/macro.subtitles.get?format=json&namespace=lyrics_richsynched&subtitle_format=mxm&app_id={APP_ID}"

TOKEN_FILE    = "musix_token.json"
INPUT_FILE    = "234.xlsx"
OUTPUT_FILE   = "234_with_lyrics.xlsx"

HEADERS = {
    "authority": "apic-desktop.musixmatch.com",
    "cookie":    "AWSELBCORS=0; AWSELB=0;",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
}

# ── токен ─────────────────────────────────────────────────────────────────────

def get_token() -> str:
    """Запрашивает новый токен и сохраняет в файл."""
    r = requests.get(TOKEN_URL, headers=HEADERS, timeout=30)
    data = r.json()
    token = data["message"]["body"]["user_token"]
    payload = {"user_token": token, "expiration_time": int(time.time()) + 600}
    with open(TOKEN_FILE, "w") as f:
        json.dump(payload, f)
    print(f"  [token] новый токен получен")
    return token


def get_valid_token() -> str:
    """Возвращает действующий токен (обновляет при необходимости)."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            data = json.load(f)
        if data["expiration_time"] > int(time.time()) + 10:
            return data["user_token"]
    return get_token()


# ── поиск трека ───────────────────────────────────────────────────────────────

def search_track(name: str, artist: str, token: str) -> str | None:
    """Ищет track_id по названию и исполнителю."""
    query = f"{name} {artist}"
    url = f"{SEARCH_URL}&q={requests.utils.quote(query)}&usertoken={token}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    data = r.json()
    try:
        tracks = data["message"]["body"]["macro_result_list"]["track_list"]
        if tracks:
            return str(tracks[0]["track"]["track_id"])
    except (KeyError, IndexError, TypeError):
        pass
    return None


# ── метод 1: через track_id (LRC subtitle) ────────────────────────────────────

def get_lyrics_by_id(track_id: str, token: str) -> str | None:
    url = f"{LYRICS_URL}&track_id={track_id}&usertoken={token}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    data = r.json()
    try:
        lrc = data["message"]["body"]["subtitle"]["subtitle_body"]
        if lrc and len(lrc.strip()) > 10:
            return lrc_to_plain(lrc)
    except (KeyError, TypeError):
        pass
    return None


# ── метод 2: macro.subtitles.get (альтернативный, без track_id) ───────────────

def get_lyrics_alternative(name: str, artist: str, token: str) -> str | None:
    url = (
        f"{LYRICS_ALT}"
        f"&usertoken={token}"
        f"&q_album="
        f"&q_artist={requests.utils.quote(artist)}"
        f"&q_artists={requests.utils.quote(artist)}"
        f"&q_track={requests.utils.quote(name)}"
    )
    r = requests.get(url, headers=HEADERS, timeout=30)
    data = r.json()
    try:
        sub = (
            data["message"]["body"]["macro_calls"]
                ["track.subtitles.get"]["message"]["body"]
                ["subtitle_list"][0]["subtitle"]["subtitle_body"]
        )
        if sub:
            return lrc_to_plain(sub)
    except (KeyError, IndexError, TypeError):
        pass
    return None


# ── LRC → plain text ──────────────────────────────────────────────────────────

def lrc_to_plain(lrc: str) -> str:
    """
    Принимает строку в LRC-формате ([mm:ss.xx]текст) или
    JSON-массив Musixmatch и возвращает чистый текст песни.
    """
    # Если это JSON-массив (subtitle_body бывает JSON-строкой)
    if lrc.strip().startswith("[{"):
        try:
            items = json.loads(lrc)
            lines = []
            for item in items:
                txt = item.get("text", "").strip()
                if txt:
                    lines.append(txt)
            result = "\n".join(lines)
            if result.strip():
                return result
        except json.JSONDecodeError:
            pass

    # Иначе — классический LRC
    plain_lines = []
    for line in lrc.splitlines():
        # убираем временны́е метки [mm:ss.xx]
        text = re.sub(r"\[\d{2}:\d{2}\.\d{2,3}\]", "", line).strip()
        # убираем музыкальный знак-заполнитель
        if text and text != "♪":
            plain_lines.append(text)
    return "\n".join(plain_lines)


# ── основная логика для одной песни ──────────────────────────────────────────

def fetch_lyrics(name: str, artist: str) -> tuple[str | None, str | None]:
    """
    Пробует два метода:
      1. Поиск → track_id → LRC subtitle
      2. macro.subtitles.get (альтернативный, напрямую по метаданным)
    Возвращает (текст, метод) или (None, None).
    """
    token = get_valid_token()

    # Метод 1
    try:
        track_id = search_track(name, artist, token)
        if track_id:
            lyrics = get_lyrics_by_id(track_id, token)
            if lyrics and len(lyrics.strip()) > 30:
                return lyrics.strip(), "musixmatch_lrc"
    except Exception as e:
        print(f"    [метод1] ошибка: {e}")

    time.sleep(0.5)

    # Метод 2
    try:
        lyrics = get_lyrics_alternative(name, artist, token)
        if lyrics and len(lyrics.strip()) > 30:
            return lyrics.strip(), "musixmatch_alt"
    except Exception as e:
        print(f"    [метод2] ошибка: {e}")

    return None, None


# ── главный цикл ──────────────────────────────────────────────────────────────

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"Файл '{INPUT_FILE}' не найден. "
        "Положите скрипт в ту же папку, что и таблица."
    )

df = pd.read_excel(INPUT_FILE)

# добавляем колонки если нет
for col in ("lyrics", "lyrics_source"):
    if col not in df.columns:
        df[col] = None

# подгружаем уже сохранённый прогресс
if os.path.exists(OUTPUT_FILE):
    df_saved = pd.read_excel(OUTPUT_FILE)
    for col in ("lyrics", "lyrics_source"):
        if col in df_saved.columns:
            df[col] = df_saved[col]
    print(f"Продолжаем с сохранённого прогресса ({OUTPUT_FILE})\n")

total   = len(df)
found   = 0
missing = []

for i, row in df.iterrows():
    if i < 550: 
        print(i)
        continue
    name   = str(row["name"]).strip()
    artist = str(row["artist"]).strip()

    # пропускаем уже найденные
    existing = df.at[i, "lyrics"]
    if pd.notna(existing) and str(existing).strip() not in ("", "nan"):
        print(f"[{i+1}/{total}] ПРОПУСК (уже есть): {artist} — {name}")
        found += 1
        continue

    print(f"[{i+1}/{total}] Ищем: {artist} — {name}")
    lyrics, source = fetch_lyrics(name, artist)

    if lyrics:
        df.at[i, "lyrics"]        = lyrics
        df.at[i, "lyrics_source"] = source
        found += 1
        print(f"    ✓ найдено ({source})")
    else:
        df.at[i, "lyrics_source"] = "NOT FOUND"
        missing.append(f"{artist} — {name}")
        print(f"    ✗ не найдено")

    # сохраняем после каждой песни
    df.to_excel(OUTPUT_FILE, index=False)
    time.sleep(1.2)   # пауза между запросами

print(f"\n{'='*60}")
print(f"Готово: {found}/{total} текстов найдено.")
if missing:
    print(f"\nНе найдено ({len(missing)}):")
    for s in missing:
        print(f"  • {s}")
print(f"\nРезультат: {OUTPUT_FILE}")