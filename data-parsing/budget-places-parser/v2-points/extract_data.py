import pdfplumber
import pandas as pd

def extract_budget_data(pdf_path):
    budget_data = []
    start_collecting = False
    budget_section_end = False

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            
            if "БЮДЖЕТНЫЕ МЕСТА" in text: start_collecting = True
            
            if "ПЛАТНЫЕ МЕСТА" in text:
                budget_section_end = True
                break
                
            if start_collecting and not budget_section_end:
                tables = page.extract_tables()
                for table in tables:
                    if len(table) > 1 and len(table[0]) > 1:
                        for row in table:
                            if "Наименование направления" in str(row[0]): continue
                            if len(row) > 1 and row[0] and row[0].strip(): budget_data.append(row[:2])
    
    columns = [
        "Направление подготовки",
        "Очная форма",
    ]
    df = pd.DataFrame(budget_data, columns=columns)
    
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.replace("", pd.NA, inplace=True)
    
    return df

pdf_path = "2024.pdf"
budget_df = extract_budget_data(pdf_path)

budget_df.to_csv("budget_places_2024.csv", index=False, encoding="utf-8-sig")

print("Данные успешно извлечены. Сохранено в budget_places_2021.csv")
