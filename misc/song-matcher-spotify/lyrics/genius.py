from lyricsgenius import Genius
import pandas as pd
from tqdm import tqdm

genius = Genius("bA8OlW3X4AgU1nlgoDc85ujT2j6hfJms9Yug9Lt5cWpuWdE1sTJ9GC7mHmUa-iJX")
table = "songs_with_genius2.xlsx"
df = pd.read_excel(table)

df.columns = df.columns.str.strip()

if "lyrics" not in df.columns:
    df["lyrics"] = ""
df["lyrics"] = df["lyrics"].astype(object)

remaining = df[df["lyrics"].isna() | (df["lyrics"] == "")].index

with tqdm(total=len(remaining), desc="Fetching lyrics") as pbar:
    for count, index in enumerate(remaining, 1):
        row = df.loc[index]
        try:
            song = genius.search_song(song_id=row["genius_id"])
            df.at[index, "lyrics"] = song.lyrics if song else ""
        except Exception as e:
            df.at[index, "lyrics"] = f"Error: {str(e)}"

        pbar.update(1)

        if count % 50 == 0:
            df.to_excel(table, index=False)
            tqdm.write(f"💾 Saved at song {count}")

df.to_excel(table, index=False)
tqdm.write("✅ Done! Final save complete.")