import pandas as pd

def task1(csv_file):
    df = pd.read_csv(csv_file)
    print(df)
    return df

def task2():
    books = [
        {'title': 'War and peace', 'author': 'Tolstoy', 'year': 1869},
        {'title': '1984', 'author': 'Orwell', 'year': 1949}
    ]
    df = pd.DataFrame(books)
    df = df.to_csv("books.csv", index=False)
    print(pd.read_csv("books.csv"))
    return df

def task3(csv_file):
    df = pd.read_csv(csv_file)
    filtered_df = df[df['Summ'] > 1000]
    print(filtered_df)
    return filtered_df

def task4(csv_file):
    df = pd.read_csv(csv_file)
    subjects = df.columns[1:]
    
    for subject in subjects:
        average_grade = df[subject].mean()
        print(f"{subject}: {average_grade:.2f}")
    return 0

def task5(csv_file1, csv_file2):
    df1 = pd.read_csv(csv_file1)
    df2 = pd.read_csv(csv_file2)
    df = pd.concat([df1, df2], ignore_index=True)
    df.to_csv("combined_file.csv")
    return 0 

# task1("prac2\\students.csv")
# task2()
# task3("prac2\\sales.csv")
# task4("prac2\\grades.csv")
task5("prac2\\file1.csv", "prac2\\file2.csv")