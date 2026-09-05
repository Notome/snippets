import pandas as pd
import matplotlib.pyplot as plt

# Загрузка данных
data = pd.read_csv('all_specialties_combined.csv')

# Список годов
years = ['2019', '2020', '2021', '2022', '2023', '2024']

# Создаем DataFrame для агрегированных данных
agg_data = pd.DataFrame(index=years, columns=['avg_points', 'sum_places', 'sum_contest'])

# Заполняем агрегированные данные
for year in years:
    points_col = f'{year}points'
    places_col = f'{year}allplaces'
    contest_col = f'{year}contest'
    
    # Средний балл (игнорируем NaN)
    avg_points = data[points_col].mean()
    
    # Сумма мест (игнорируем NaN)
    sum_places = data[places_col].sum()
    
    # Сумма конкурса (игнорируем NaN)
    sum_contest = data[contest_col].sum()
    
    agg_data.loc[year] = [avg_points, sum_places, sum_contest]

# Создаем фигуру с тремя графиками
plt.figure(figsize=(15, 10))

# График 1: Средний балл по всем направлениям
plt.subplot(3, 1, 1)
plt.plot(agg_data.index, agg_data['avg_points'], marker='o', color='blue', label='Средний балл')
plt.title('Средний балл по всем направлениям за годы')
plt.ylabel('Баллы')
plt.grid(True)
plt.legend()

# График 2: Сумма мест по всем направлениям
plt.subplot(3, 1, 2)
plt.plot(agg_data.index, agg_data['sum_places'], marker='o', color='green', label='Сумма мест')
plt.title('Общее количество мест по всем направлениям за годы')
plt.ylabel('Количество мест')
plt.grid(True)
plt.legend()

# График 3: Сумма конкурса по всем направлениям
plt.subplot(3, 1, 3)
plt.plot(agg_data.index, agg_data['sum_contest'], marker='o', color='red', label='Сумма конкурса')
plt.title('Общий конкурс по всем направлениям за годы')
plt.ylabel('Конкурс (чел./место)')
plt.xlabel('Год')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()