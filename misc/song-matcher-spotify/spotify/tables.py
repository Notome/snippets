import re
import pandas as pd

df_all = pd.read_excel("notfound.xlsx", header=0)
df_founded = pd.read_excel("found.xlsx")
df_founded = df_founded[[c for c in df_founded.columns if not c.startswith('Unnamed')]]

def clean_text(s):
    return str(s).strip().lower() if pd.notna(s) else ""

def remove_brackets(s):
    """Убирает всё начиная с первой открывающей скобки (круглой, квадратной или фигурной)"""
    if pd.isna(s):
        return s
    return re.sub(r'\s*[\(\[\{].*', '', str(s)).strip()

def extract_first_artist(artists):
    if pd.isna(artists):
        return ""
    for sep in [';', '/', 'feat', '&', ',']:
        if sep in str(artists):
            return str(artists).split(sep)[0].strip().lower()
    return str(artists).strip().lower()

# Применяем удаление скобок к Track_Name в обоих датафреймах
df_all['Track_Name'] = df_all['Track_Name'].apply(remove_brackets)
df_founded['Track_Name'] = df_founded['Track_Name'].apply(remove_brackets)

df_all['_track'] = df_all['Track_Name'].apply(clean_text)
df_all['_artist'] = df_all['Artist_Name'].apply(extract_first_artist)

df_founded['_track'] = df_founded['Track_Name'].apply(clean_text)
df_founded['_artist'] = df_founded['Artist_Name'].apply(extract_first_artist)

founded_dedup = df_founded.drop_duplicates(subset=['_track', '_artist'])

founded_data_cols = [c for c in founded_dedup.columns if c not in ['Track_Name', 'Artist_Name', '_track', '_artist']]

df_all.drop(columns=[c for c in founded_data_cols if c in df_all.columns], inplace=True)

founded_merge = founded_dedup[['_track', '_artist'] + founded_data_cols]

df_result = df_all.merge(founded_merge, on=['_track', '_artist'], how='left')

df_result.drop(columns=['_track', '_artist'], inplace=True)

if 'Release Date' in df_result.columns:
    df_result['Release Date'] = (
        pd.to_datetime(df_result['Release Date'], errors='coerce')
        .dt.year.astype('Int64').astype(str).replace('<NA>', '')
    )

df_result.rename(columns={'Release Date': 'Release_Date'}, inplace=True)

df_result.to_excel("result.xlsx", index=False)
print(f"Done: {len(df_result)} rows, {df_result[founded_data_cols[0]].notna().sum() if founded_data_cols else 0} matched")