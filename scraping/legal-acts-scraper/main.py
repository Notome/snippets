import requests
from bs4 import BeautifulSoup

lst = []

for page in range(1, 20):
    url = f"https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&p={page}&region=1&room1=1&type=4"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    prices = soup.find_all("span", {"data-testid": "card.price"})

    for price in prices:
        try: 
            price_text = price.get_text(strip=True)
            cleaned_price = price_text.replace('₽/мес.', '').replace('\xa0', '').strip()
            lst.append(int(cleaned_price))
        except Exception as e:
            print(f"Ошибка обработки цены: {e}")
            continue

print(f"Средняя стоимость {sum(lst) / len(lst)}")