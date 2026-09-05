import json

def task1():
    student = {"name": "Анна", "age": 21, "grades": [4, 5, 4, 3, 5]}

    json_str = json.dumps(student, ensure_ascii=False, indent=4)
    print(json_str)
    return json_str


def task2(filename="data.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            print(f"Имя студента: {data['name']}")
            return data["name"]
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return None


def task3(filename="data.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        data["email"] = "ivan@example.com"

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("Файл успешно обновлен!")
        print(json.dumps(data, ensure_ascii=False, indent=4))
        return data
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return None


def task4():
    books = [
        {"title": "Преступление и наказание", "author": "Достоевский", "year": 1866},
        {"title": "Война и мир", "author": "Толстой", "year": 1869},
        {"title": "Мастер и Маргарита", "author": "Булгаков", "year": 1967},
        {"title": "Идиот", "author": "Достоевский", "year": 1869},
        {"title": "Анна Каренина", "author": "Толстой", "year": 1877},
    ]

    with open("books.json", "w", encoding="utf-8") as file:
        json.dump(books, file, ensure_ascii=False, indent=4)

    print("Файл books.json создан!")

    def find_books_by_author(author_name):
        with open("books.json", "r", encoding="utf-8") as file:
            books_data = json.load(file)

        found_books = [
            book for book in books_data if book["author"].lower() == author_name.lower()
        ]
        return found_books

    author = "Достоевский"
    found = find_books_by_author(author)
    print(f"\nКниги автора '{author}':")
    for book in found:
        print(f"- {book['title']} ({book['year']})")

    return find_books_by_author


def task5(filename="nonexistent.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        print("Файл успешно прочитан!")
        return data
    except FileNotFoundError:
        print(f"Ошибка: Файл {filename} не найден!")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка: Файл {filename} содержит некорректный JSON!")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return None


def task6():
    temperatures_json = [
        {"date": "2025-10-01", "temperature": -5},
        {"date": "2025-10-02", "temperature": -3},
        {"date": "2025-10-03", "temperature": -7},
        {"date": "2025-10-04", "temperature": -2},
        {"date": "2025-10-05", "temperature": 0},
    ]

    temperatures_dict = {
        item["date"]: item["temperature"] for item in temperatures_json
    }

    print("Исходный JSON:")
    print(json.dumps(temperatures_json, ensure_ascii=False, indent=2))
    print("\nПреобразованный словарь:")
    print(temperatures_dict)

    return temperatures_dict


def task7():
    catalog = {
        "Электроника": {
            "Смартфоны": [
                {"name": "iPhone 15", "price": 999, "brand": "Apple"},
                {"name": "Galaxy S24", "price": 899, "brand": "Samsung"},
            ],
            "Ноутбуки": [
                {"name": "MacBook Pro", "price": 1999, "brand": "Apple"},
                {"name": "ThinkPad X1", "price": 1499, "brand": "Lenovo"},
            ],
        },
        "Книги": {
            "Художественная литература": [
                {"name": "1984", "price": 15, "author": "Оруэлл"},
                {"name": "Мастер и Маргарита", "price": 12, "author": "Булгаков"},
            ],
            "Научная литература": [
                {"name": "Краткая история времени", "price": 20, "author": "Хокинг"}
            ],
        },
    }

    with open("catalog.json", "w", encoding="utf-8") as file:
        json.dump(catalog, file, ensure_ascii=False, indent=4)

    print("Каталог товаров создан в файле catalog.json")

    def find_product(product_name):
        with open("catalog.json", "r", encoding="utf-8") as file:
            catalog_data = json.load(file)

        results = []

        def search_in_category(category):
            if isinstance(category, dict):
                for key, value in category.items():
                    if isinstance(value, list):
                        for item in value:
                            if (
                                isinstance(item, dict)
                                and item.get("name", "").lower() == product_name.lower()
                            ):
                                results.append({"product": item, "category": key})
                    else:
                        search_in_category(value)

        for main_category, subcategories in catalog_data.items():
            search_in_category(subcategories)

        return results

    product_name = "iPhone 15"
    found_products = find_product(product_name)

    if found_products:
        print(f"\nНайденные товары с названием '{product_name}':")
        for item in found_products:
            print(
                f"- {item['product']['name']} (Цена: ${item['product']['price']}, Категория: {item['category']})"
            )
    else:
        print(f"\nТовар '{product_name}' не найден.")

    return find_product


def create_initial_files():
    initial_data = {"name": "Иван", "age": 20, "courses": ["Математика", "Физика"]}

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(initial_data, file, ensure_ascii=False, indent=4)

    print("Создан файл data.json для демонстрации")


if __name__ == "__main__":
    create_initial_files()

    # json_data = task1()
    # task2()
    # task3()
    # find_books_func = task4()
    # task5()
    # task5("data.json")
    # task6()
    find_product_func = task7()
