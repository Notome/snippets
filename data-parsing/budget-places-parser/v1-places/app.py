import tabula
import pandas as pd

# Список областей для извлечения (из вашего JSON)
regions = [
    {"page": 1, "method": "lattice", "area": [218.37, 110.08, 566.72, 487.89]},
    {"page": 2, "method": "guess", "area": [27.89, 109.03, 565.66, 486.84]},
    {"page": 3, "method": "lattice", "area": [28.94, 110.08, 515.15, 487.89]},
]

# Создаём Excel-файл
all_dfs = []  # Список для хранения всех DataFrame

for region in regions:
    df = tabula.read_pdf(
        "2020.pdf",
        pages=region["page"],
        area=region["area"],
        lattice=(region["method"] == "lattice"),
        stream=(region["method"] != "lattice"),
        guess=(region["method"] == "guess"),
        silent=True,
    )
    
    if df:
        all_dfs.append(df[0])

# Объединяем все таблицы в один DataFrame
combined_df = pd.concat(all_dfs, ignore_index=True)

# Сохраняем в Excel
combined_df.to_excel("2020.xlsx", index=False)
print("Готово! Все таблицы объединены в combined_output.xlsx")