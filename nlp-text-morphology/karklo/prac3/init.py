import pandas as pd
import numpy as np

data = {
    'date': pd.date_range('2023-01-01', periods=100),
    'city': np.random.choice(['Москва', 'СПб', 'Екатеринбург'], 100),
    'category': np.random.choice(['Электроника', 'Одежда', 'Продукты'], 100),
    'product_id': np.random.randint(1000, 2000, 100),
    'sales': np.random.randint(1000, 30000, 100),
    'quantity': np.random.randint(1, 10, 100),
    'price': np.random.randint(500, 5000, 100)
}

df = pd.DataFrame(data)
df.to_csv('sales.csv', index=False)