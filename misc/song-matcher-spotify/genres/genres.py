import anthropic
import pandas as pd
import os
import time

client = 
df = pd.read_excel("genres_bd.xlsx")

SYSTEM_PROMPT = """You are a music genre classification assistant.
Given a track name and artist, return ONLY the genre name (e.g. 'Pop', 'Hip-Hop', 'Jazz').
If unknown, return 'Unknown'. No explanation, just the genre."""

def classify_track(name, artist, retries=3):
    for attempt in range(retries):
        try:
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=20,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"Track: {name}\nArtist: {artist}"}]
            )
            return msg.content[0].text.strip()
        except anthropic.RateLimitError:
            wait = 2 ** attempt
            print(f"Rate limited, waiting {wait}s...")
            time.sleep(wait)
    return "Error"

if "genre" not in df.columns:
    df["genre"] = None

genres = df["genre"].tolist()

for i, row in df.iterrows():
    if pd.notna(genres[i]):
        continue

    genres[i] = classify_track(row['name'], row['artist 1'])

    if i % 100 == 0:
        print(f"Progress: {i}/{len(df)}")

    if (i + 1) % 50 == 0:
        df["genre"] = genres
        df.to_excel("genres_bd_classified.xlsx", index=False)
        print(f"Saved at row {i + 1}")

    time.sleep(0.1)

df["genre"] = genres
df.to_excel("genres_bd_classified.xlsx", index=False)
print("Done!")