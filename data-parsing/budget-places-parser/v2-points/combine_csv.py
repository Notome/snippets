import pandas as pd
import numpy as np

files = [
    'budget_places_2019.csv',
    'budget_places_2020.csv',
    'budget_places_2021.csv',
    'budget_places_2022.csv',
    'budget_places_2023.csv',
    'budget_places_2024.csv'
]

all_names = set()
for file in files:
    df = pd.read_csv(file)
    all_names.update(df['name'].unique())

data_dict = {name: {} for name in all_names}

for year, file in enumerate(files, start=2019):
    df = pd.read_csv(file)
    for _, row in df.iterrows():
        name = row['name']
        data_dict[name][year] = row['points']

result = []
for name in sorted(all_names):
    row_data = {'name': name}
    for year in range(2019, 2025):
        row_data[str(year)] = data_dict[name].get(year, np.nan)
    result.append(row_data)

final_df = pd.DataFrame(result)

final_df.to_csv('all_specialties_combined.csv', index=False)

print("Все специальности за 2019-2024 годы:")
print(final_df.to_string(index=False))