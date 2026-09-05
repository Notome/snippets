import pandas as pd
import requests
import time
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Отключаем предупреждения об SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

df = pd.read_excel("234.xlsx")

if 'text' not in df.columns:
    df['text'] = ''

url = "https://yourserver.com/getLyricsMusix.php"

# Настраиваем сессию с retry-логикой
session = requests.Session()

retry_strategy = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

for idx, row in df.iterrows():
    # Пропускаем уже заполненные строки
    if pd.notna(df.at[idx, 'text']) and str(df.at[idx, 'text']).strip():
        print(f"{row['name']} ({idx}) SKIP (already has lyrics)")
        continue

    try:
        params = {
            "q": f"{row['name']} {row['artist']}",
            "type": "default"
        }

        resp = session.get(
            url,
            params=params,
            timeout=15,
            verify=False  # Отключаем проверку SSL-сертификата
        )

        if resp.status_code == 200 and resp.text.strip():
            # Проверяем, что это не JSON с ошибкой
            if '"isError":true' not in resp.text:
                df.at[idx, 'text'] = resp.text
                print(f"{row['name']} ({idx}) +")
            else:
                df.at[idx, 'text'] = ''
                print(f"{row['name']} ({idx}) - (API error: {resp.text[:80]})")
        else:
            df.at[idx, 'text'] = ''
            print(f"{row['name']} ({idx}) - (status: {resp.status_code})")

    except requests.exceptions.SSLError:
        # Фолбэк на HTTP если SSL не работает
        try:
            http_url = url.replace("https://", "http://")
            resp = session.get(http_url, params=params, timeout=15)
            if resp.status_code == 200 and resp.text.strip():
                df.at[idx, 'text'] = resp.text
                print(f"{row['name']} ({idx}) + (via HTTP fallback)")
            else:
                df.at[idx, 'text'] = ''
                print(f"{row['name']} ({idx}) - (HTTP fallback failed)")
        except Exception as e2:
            df.at[idx, 'text'] = ''
            print(f"{row['name']} ({idx}) ERROR (SSL + HTTP fallback): {e2}")

    except Exception as e:
        df.at[idx, 'text'] = ''
        print(f"{row['name']} ({idx}) ERROR: {e}")

    # Сохраняем прогресс каждые 10 треков
    if idx % 10 == 0:
        df.to_excel("234_with_lyrics.xlsx", index=False)
        print(f"--- Progress saved at index {idx} ---")

    time.sleep(1.5)  # Немного увеличили паузу

# Финальное сохранение
df.to_excel("234_with_lyrics.xlsx", index=False)
print("Done!")