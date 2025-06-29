import pandas as pd

CSV_FILE = "results_batch.csv"
SQL_FILE = "import_data.sql"

def sql_escape(val):
    if pd.isnull(val):
        return None
    return str(val).replace("\\", "\\\\").replace("'", "''")

def unique_dict(series):
    """Assign unique IDs to non-null unique values in a series."""
    vals = [v for v in series if pd.notnull(v)]
    unique_vals = []
    seen = set()
    for v in vals:
        if v not in seen:
            unique_vals.append(v)
            seen.add(v)
    return {v: i+1 for i, v in enumerate(unique_vals)}

# Load CSV
df = pd.read_csv(CSV_FILE)

# Extract unique values for lookup tables
author_map = unique_dict(df['Autor'])
publisher_map = unique_dict(df['Wydawca'])
category_map = unique_dict(df['Kategoria'])
department_map = unique_dict(df['Dział'])
language_map = unique_dict(df['Język'])

# Prepare insert statements for lookup tables
authors_sql = [f"INSERT INTO authors (id, name) VALUES ({i}, '{sql_escape(name)}');"
               for name, i in author_map.items()]

publishers_sql = [f"INSERT INTO publishers (id, name) VALUES ({i}, '{sql_escape(name)}');"
                  for name, i in publisher_map.items()]

categories_sql = [f"INSERT INTO categories (id, name) VALUES ({i}, '{sql_escape(name)}');"
                  for name, i in category_map.items()]

departments_sql = [f"INSERT INTO departments (id, name) VALUES ({i}, '{sql_escape(name)}');"
                   for name, i in department_map.items()]

languages_sql = [f"INSERT INTO languages (id, name) VALUES ({i}, '{sql_escape(name)}');"
                 for name, i in language_map.items()]

# Prepare insert statements for products
products_sql = []
for idx, row in df.iterrows():
    author_id = author_map.get(row['Autor']) if pd.notnull(row['Autor']) else 'NULL'
    publisher_id = publisher_map.get(row['Wydawca']) if pd.notnull(row['Wydawca']) else 'NULL'
    category_id = category_map.get(row['Kategoria']) if pd.notnull(row['Kategoria']) else 'NULL'
    department_id = department_map.get(row['Dział']) if pd.notnull(row['Dział']) else 'NULL'
    language_id = language_map.get(row['Język']) if pd.notnull(row['Język']) else 'NULL'

    def v(field):
        return f"'{sql_escape(row[field])}'" if pd.notnull(row[field]) else "NULL"

    liczba_stron = None
    if pd.notnull(row['Liczba stron']):
        try:
            liczba_stron = int(row['Liczba stron'])
        except Exception:
            liczba_stron = f"'{sql_escape(row['Liczba stron'])}'"
    else:
        liczba_stron = "NULL"

    products_sql.append(
        "INSERT INTO products (link, tytul, tytul_orginalu, author_id, publisher_id, "
        "category_id, department_id, language_id, rodzaj_nosnik, rodzaj_oprawy, "
        "rok_wydania, wymiary, liczba_stron, ciezar, wydano, isbn, ean_upc, image, description) VALUES ("
        f"{v('Link')}, {v('Tytuł')}, {v('Tytuł originału')}, {author_id}, {publisher_id}, "
        f"{category_id}, {department_id}, {language_id}, {v('Rodzaj (nośnik)')}, {v('Rodzaj oprawy')}, "
        f"{v('Rok wydania')}, {v('Wymiary')}, {liczba_stron}, {v('Ciężar')}, {v('Wydano')}, "
        f"{v('ISBN')}, {v('EAN/UPC')}, {v('Image')}, {v('Description')});"
    )

# Write to SQL file
with open(SQL_FILE, "w", encoding="utf-8") as f:
    f.write("-- Authors\n" + "\n".join(authors_sql) + "\n\n")
    f.write("-- Publishers\n" + "\n".join(publishers_sql) + "\n\n")
    f.write("-- Categories\n" + "\n".join(categories_sql) + "\n\n")
    f.write("-- Departments\n" + "\n".join(departments_sql) + "\n\n")
    f.write("-- Languages\n" + "\n".join(languages_sql) + "\n\n")
    f.write("-- Products\n" + "\n".join(products_sql) + "\n\n")

print(f"SQL import file generated: {SQL_FILE}")
