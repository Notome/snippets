from nltk.stem import PorterStemmer
import string 

def my_stemmer():
    words = []
    with open('text.txt', 'r', encoding="utf-8") as text:
        line = text.read().split()
        for word in line:
            words.append(word.translate(str.maketrans('', '', string.punctuation + '»— \n\t')))
    
    ps = PorterStemmer()
    words = list(set(words))
    
    with open("stemmer.txt", 'w', encoding="utf-8") as writable:
        for w in words:
            rootWord = ps.stem(w)
            writable.write(rootWord + ' ')

if __name__ == "__main__":
    my_stemmer()