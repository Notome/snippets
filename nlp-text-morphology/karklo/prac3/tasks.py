import pandas as pd
import numpy as np

def task1():
    df = pd.read_csv('prac3\sales.csv')
    print("Первые 5 строк:")
    print(df.head())
    print("\nПроверка пропущенных значений:")
    print(df.isnull().sum())
    print("\nОсновная статистика по числовым столбцам:")
    print(df.describe())
    return df
task1()

def task2():
    df = pd.read_csv('prac3\sales.csv')
    df['date'] = pd.to_datetime(df['date'])

    print("Строки где продажи больше 1000:")
    filtered_sales = df[df['sales'] > 1000]
    print(filtered_sales)

    print("\nЗаписи за январь 2023:")
    january_data = df[(df['date'] >= '2023-01-01') & (df['date'] <= '2023-01-31')]
    print(january_data)

    print("\nФильтр по нескольким условиям (Москва и Электроника):")
    multi_filter = df[(df['city'] == 'Москва') & (df['category'] == 'Электроника')]
    print(multi_filter)

    return df
task2()

def task3():
    df = pd.read_csv('prac3\sales.csv')

    print("Суммарные продажи по городам:")
    city_sales = df.groupby('city')['sales'].sum()
    print(city_sales)

    print("\nСредний чек по категориям товаров:")
    df['average_check'] = df['sales'] / df['quantity']
    avg_check_by_category = df.groupby('category')['average_check'].mean()
    print(avg_check_by_category)

    print("\nТоп-5 товаров по объему покупок:")
    top_products = df.groupby('product_id')['sales'].sum().nlargest(5)
    print(top_products)

    return df

task3()

def task4():
    df = pd.read_csv('prac3\sales.csv')

    print("Исходные данные с пропусками:")
    print(df.isnull().sum())

    df_with_nan = df.copy()
    df_with_nan.loc[::10, 'sales'] = np.nan

    print("\nДанные после создания пропусков:")
    print(df_with_nan.isnull().sum())

    print("\nЗаполнение пропусков средним значением:")
    df_filled = df_with_nan.copy()
    df_filled['sales'] = df_filled['sales'].fillna(df_filled['sales'].mean())
    print(df_filled.isnull().sum())

    print("\nУдаление строк с пропущенными данными:")
    df_dropped = df_with_nan.dropna()
    print(f"Количество строк после удаления: {len(df_dropped)}")

    print("\nСоздание нового столбца на основе существующих:")
    df['total_revenue'] = df['sales'] * df['quantity']
    print(df[['sales', 'quantity', 'total_revenue']].head())

    return df
task4()

def task5():
    df = pd.read_csv('prac3\sales.csv')

    print("Общая статистика по месяцам:")
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    monthly_stats = df.groupby('month').agg({
        'sales': ['sum', 'mean', 'count'],
        'quantity': 'sum'
    })
    print(monthly_stats)

    print("\nДоля продаж по категориям:")
    category_share = df.groupby('category')['sales'].sum() / df['sales'].sum() * 100
    print(category_share)

    print("\nСводная таблица: продажи по городам и категориям")
    pivot_table = df.pivot_table(values='sales', index='city', columns='category', aggfunc='sum')
    print(pivot_table)

    return df
task5()