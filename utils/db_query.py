
import mysql.connector
def fetch_query_data(query):
    MYSQL_CONFIG={
         'host': "localhost",
         'user': 'aadarsh',
         'password': 'S@feP@ssw0rd2025!',
         'database': 'praveshan'
    }
    try:

        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)

        headers = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        return headers, rows

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return [], []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    # Example usage
    query = "SELECT * FROM Movies LIMIT 10;"
    headers, rows = fetch_query_data(query)
    print("Headers:", headers)
    print("Rows:", rows)