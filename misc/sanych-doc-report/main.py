from docx import Document
import pandas as pd

doc = Document('document.docx')

full_text = []
for para in doc.paragraphs:
    full_text.append(para.text)

authors = []
songs = []

for x in full_text:
    if x.strip().startswith('Респондент:'):
        continue
    if ' — ' not in x: continue 
    idx = x.index(' — ')        
    
    song_part = x[: idx].strip()
    author_part = x[idx+2:].strip()
    
    authors.append(song_part)
    songs.append(author_part)

df = pd.DataFrame({
    'author': authors,
    'song': songs
})

df.to_excel('table.xlsx')