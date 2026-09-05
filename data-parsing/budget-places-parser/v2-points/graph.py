import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv(r'C:\Users\dron\Desktop\points\all_specialties_combined.csv')

years = [2019, 2020, 2021, 2022, 2023, 2024]

plt.figure(figsize=(15, 10))

for i, row in df.iterrows():
    specialty_name = row['name']
    points = row[['2019', '2020', '2021', '2022', '2023', '2024']].values
    
    points = [float(x) if str(x).lower() != 'nan' and not pd.isna(x) else np.nan for x in points]
    
    segments = []
    current_segment = []
    for year, point in zip(years, points):
        if not np.isnan(point):
            current_segment.append((year, point))
        elif current_segment:
            segments.append(current_segment)
            current_segment = []
    if current_segment:
        segments.append(current_segment)
    
    for segment in segments:
        x_vals, y_vals = zip(*segment)
        plt.plot(x_vals, y_vals, marker='o', label=specialty_name if segment == segments[0] else "")
        specialty_name = ""

plt.title('Динамика проходных баллов по специальностям (2019-2024)', fontsize=14)
plt.xlabel('Год', fontsize=12)
plt.ylabel('Проходной балл', fontsize=12)
plt.xticks(years)
plt.grid(True, linestyle='--', alpha=0.7)

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., fontsize=8)

plt.tight_layout()
plt.show()