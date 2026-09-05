import requests
import pandas as pd
import time
import os
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

SAVE_EVERY = 50
BATCH_SIZE = 90       # запросов до принудительной паузы
BATCH_PAUSE = 90      # секунд отдыха между батчами
OUTPUT_FILE = "songs_with_genius.xlsx"
TOKEN = os.getenv("GENIUS_API_TOKEN")
DELAY = 0.5
MAX_RETRIES = 3


def get_song_info(session, name, artist):
    url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    params = {"q": f"{name} {artist}"}

    for attempt in range(MAX_RETRIES):
        try:
            resp = session.get(url, headers=headers, params=params, timeout=15)

            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 60))
                print(f"\n⚠️  Rate limit! Пауза {wait}s...")
                time.sleep(wait)
                continue

            if resp.status_code != 200:
                print(f"\nHTTP {resp.status_code} для '{name}', попытка {attempt + 1}")
                time.sleep(2 ** attempt)
                continue

            if "text/html" in resp.headers.get("Content-Type", ""):
                wait = 30 * (attempt + 1)
                print(f"\n🚫 HTML вместо JSON для '{name}' — пауза {wait}s")
                time.sleep(wait)
                continue

            data = resp.json()
            hits = data["response"]["hits"]

            if hits:
                r = hits[0]["result"]
                return {"id": r["id"], "url": r["url"]}
            return "not_found"

        except requests.RequestException as e:
            print(f"\nОшибка '{name}' (попытка {attempt + 1}): {e}")
            time.sleep(2 ** attempt)

    return "not_found"


def main():
    if os.path.exists(OUTPUT_FILE):
        print("📂 Загружаю существующий прогресс...")
        df = pd.read_excel(OUTPUT_FILE)
        df["genius_id"] = df["genius_id"].astype(object)
    else:
        df = pd.read_excel("song_bd.xlsx")
        df["genius_id"] = None
        df["genius_url"] = None

    todo_idx = [i for i, row in df.iterrows() if pd.isna(row["genius_id"])]

    done = df["genius_id"].notna().sum()
    print(f"✅ Уже готово: {done} | ⏳ Осталось: {len(todo_idx)}")

    if not todo_idx:
        print("Всё уже обработано!")
        return

    session = requests.Session()
    counter = 0
    batch_counter = 0

    for i in tqdm(todo_idx, desc="Genius lookup"):
        name = df.loc[i, "name"]
        artist = df.loc[i, "artist"]

        result = get_song_info(session, name, artist)

        if result and result != "not_found":
            df.loc[i, "genius_id"] = result["id"]
            df.loc[i, "genius_url"] = result["url"]
        else:
            df.loc[i, "genius_id"] = "not_found"

        counter += 1
        batch_counter += 1
        time.sleep(DELAY)

        if counter % SAVE_EVERY == 0:
            print(f"\n💾 Сохраняю... ({done + counter} готово)")
            df.to_excel(OUTPUT_FILE, index=False)

        # Принудительная пауза каждые BATCH_SIZE запросов
        if batch_counter >= BATCH_SIZE:
            df.to_excel(OUTPUT_FILE, index=False)
            print(f"\n😴 Батч из {BATCH_SIZE} выполнен — отдых {BATCH_PAUSE}s...")
            time.sleep(BATCH_PAUSE)
            batch_counter = 0
            print("▶️  Продолжаем...")

    df.to_excel(OUTPUT_FILE, index=False)
    found = df[df["genius_id"].notna() & (df["genius_id"] != "not_found")].shape[0]
    print(f"\n✅ Готово! Найдено: {found}/{len(df)}")


if __name__ == "__main__":
    main()