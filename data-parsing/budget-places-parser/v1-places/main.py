from docx import Document
from collections import defaultdict

def parse_all_tables(file_path):
    doc = Document(file_path)
    tables = doc.tables
    if not tables:
        return None

    all_data = []
    
    if len(tables) > 0:
        first_table = tables[0]
        headers = []
        for cell in first_table.rows[0].cells:
            text = cell.text.strip().replace('>', '').strip()
            headers.append(text)
        
        for row in first_table.rows[1:]:
            row_data = {}
            for i, cell in enumerate(row.cells):
                text = cell.text.strip().replace('>', '').strip()
                if i < len(headers):
                    row_data[headers[i]] = text
            if row_data:
                all_data.append(row_data)

    for table in tables[1:]:
        for row in table.rows:
            cells = row.cells
            if len(cells) >= 4:
                direction = cells[2].text.strip().replace('>', '').strip()
                general_competition = cells[4].text.strip().replace('>', '').strip()
                competition_common = cells[6].text.strip().replace('>', '').strip()
                
                if direction:
                    row_data = {
                        'Направление подготовки (специальности)': direction,
                        'общий конкурс': general_competition,
                        'конкурс на общие места': competition_common
                    }
                    all_data.append(row_data)
    
    return all_data

def clean_data(data):
    cleaned_data = []
    for entry in data:
        cleaned_entry = {}
        if 'Направление подготовки (специальности)' in entry:
            cleaned_entry['Направление подготовки (специальности)'] = entry['Направление подготовки (специальности)']
        if 'общий конкурс' in entry:
            cleaned_entry['общий конкурс'] = entry.get('общий конкурс', '')
        elif 'Общий конкурс' in entry:
            cleaned_entry['общий конкурс'] = entry.get('Общий конкурс', '')
        
        if 'конкурс на общие места' in entry:
            cleaned_entry['конкурс на общие места'] = entry.get('конкурс на общие места', '')
        elif 'Конкурс на общие места' in entry:
            cleaned_entry['конкурс на общие места'] = entry.get('Конкурс на общие места', '')
        
        if cleaned_entry:
            cleaned_data.append(cleaned_entry)
    return cleaned_data

file_path = '2019.docx'
parsed_data = parse_all_tables(file_path)
cleaned_data = clean_data(parsed_data)

for entry in cleaned_data:
    print(f"Направление: {entry.get('Направление подготовки (специальности)', '')}")
    print(f"Общий конкурс: {entry.get('общий конкурс', '')}")
    print(f"Конкурс на общие места: {entry.get('конкурс на общие места', '')}")
    print("-" * 50)