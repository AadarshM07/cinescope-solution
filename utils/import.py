import csv
import mysql.connector

db_config = {
    'host': "localhost",
    'user': 'aadarsh',
    'password': 'S@feP@ssw0rd2025!',
    'database': 'praveshan'
}

csv_file = '../movie.csv'
table = 'Movies'

int_columns = ['Released_Year', 'Meta_score', 'No_of_Votes']
float_columns = ['IMDB_Rating']

def clean_value(col_name, value):
    if value == '':
        return None
    if col_name in int_columns:
        try:
            return int(value)
        except ValueError:
            return None
    if col_name in float_columns:
        try:
            return float(value)
        except ValueError:
            return None
    return value

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

with open(csv_file, 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    headers = next(reader)
    print("Columns:", headers)

    placeholders = ','.join(['%s'] * len(headers))
    columns = ','.join(headers)
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    for row in reader:
        cleaned_row = [clean_value(col, val) for col, val in zip(headers, row)]
        cursor.execute(query, cleaned_row)

conn.commit()
cursor.close()
conn.close()

print("CSV data imported into MySQL successfully.")
