import matplotlib.pyplot as plt
import numpy as np

def task1():
    x = np.linspace(-10, 10, 100)
    y = x**2
    
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.title('График функции y = x²')
    plt.xlabel('Ось X')
    plt.ylabel('Ось Y')
    plt.grid(True)
    plt.show()

def task2():
    categories = ['Электроника', 'Одежда', 'Книги', 'Продукты', 'Косметика']
    sales = [35, 25, 15, 20, 5]
    
    plt.figure(figsize=(8, 8))
    plt.pie(sales, labels=categories, autopct='%1.1f%%', startangle=90)
    plt.title('Распределение продаж по категориям товаров')
    plt.show()

def task3():
    x = np.linspace(0, 4*np.pi, 100)
    y_sin = np.sin(x)
    y_cos = np.cos(x)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y_sin, 'r-', linewidth=2, label='sin(x)')
    plt.plot(x, y_cos, 'b--', linewidth=2, label='cos(x)')
    plt.title('Графики функций синуса и косинуса')
    plt.xlabel('Ось X')
    plt.ylabel('Ось Y')
    plt.legend()
    plt.grid(True)
    plt.show()

def task4(arr = [4, 5, 3, 4, 5, 5, 4, 3, 2, 4]):
    plt.figure(figsize=(8, 6))
    plt.hist(arr, bins=30, color='skyblue', edgecolor='black')
    plt.xlabel('Значения')
    plt.ylabel('Частота')
    plt.title('Пример гистограммы')
    plt.show()

task1()
task2()
task3()
task4()