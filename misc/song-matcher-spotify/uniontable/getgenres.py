import pandas as pd

df_main = pd.read_excel("genres_bd.xlsx")
df_genres = pd.read_excel("genres_bd_uncapped.xlsx")

# Берём жанровые колонки из второй таблицы и просто добавляем справа
genre_cols = df_genres.columns[3:]
df_result = pd.concat([df_main, df_genres[genre_cols]], axis=1)

df_result.to_excel("genres_bd_final.xlsx", index=False)
print(df_result.shape)