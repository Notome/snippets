import pandas as pd

match_df = pd.read_excel("match songs.xlsx")
songs_df = pd.read_excel("songs_bd.xlsx")

if "theme_main" in songs_df.columns:
    songs_df = songs_df.rename(columns={"theme_main": "theme"})

for df in [match_df, songs_df]:
    df["artist"] = df["artist"].astype(str).str.strip().str.lower()
    df["name"] = df["name"].astype(str).str.strip().str.lower()

cols_to_fill = ["drugs", "alcohol", "explicit", "smoking", "theme"]

# ВАЖНО: разрешаем смешанные типы
for col in cols_to_fill:
    match_df[col] = match_df[col].astype("object")

songs_dict = {
    (row["artist"], row["name"]): row
    for _, row in songs_df.iterrows()
}

for i, row in match_df.iterrows():
    key = (row["artist"], row["name"])

    if key in songs_dict:
        source_row = songs_dict[key]

        for col in cols_to_fill:
            if pd.isna(row[col]) and pd.notna(source_row[col]):
                match_df.at[i, col] = source_row[col]

match_df.to_excel("matched_songs.xlsx", index=False)

print("Готово ✅")