import pandas as pd
df = pd.read_csv('tabula-2022.csv', encoding='utf-8')  # или 'windows-1251'
df.to_excel("2022.xlsx", index=False)
print(df)