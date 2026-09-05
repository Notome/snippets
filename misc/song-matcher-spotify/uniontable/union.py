import pandas as pd

df = pd.read_excel("genres_bd1.xlsx")
for i in range(2, 11):
    df_to_concat = pd.read_excel(f"genres_bd{i}.xlsx")
    df = pd.concat([df, df_to_concat], ignore_index=True)
df.to_excel("genres_bd.xlsx", index=False)
