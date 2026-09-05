import lyricsgenius
import pandas as pd
import time
import requests
from requests.exceptions import Timeout

TIMEOUT = 15
OUTPUT_FILE = "done.xlsx"

df = pd.read_excel("123.xlsx")

genius = lyricsgenius.Genius(
    "bA8OlW3X4AgU1nlgoDc85ujT2j6hfJms9Yug9Lt5cWpuWdE1sTJ9GC7mHmUa",
    timeout=TIMEOUT
)

genius.verbose = False

for idx, row in df.iterrows():
    url = row["genius_url"]
    lyrics = None
    try:
        print(f"Processing {idx}: {url}")
        lyrics = genius.lyrics(song_url=url)
        row['text'] = lyrics
        print(f"  -> Lyrics found (length: {len(lyrics) if lyrics else 0})")
    except Timeout as e:
        print(f"  -> Timeout error for {url}: {e}")
        row['text'] = f"ERROR: Request timed out after {TIMEOUT}s"
    except Exception as e:
        print(f"  -> Error for {url}: {type(e).__name__} - {e}")
        row['text'] = f"ERROR: {type(e).__name__} - {e}"

    df.at[idx, 'text'] = row['text']

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"  -> Saved to {OUTPUT_FILE}")

print("\nAll done.")