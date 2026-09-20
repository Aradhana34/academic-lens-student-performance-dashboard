from database import get_db_connection

try:
    conn = get_db_connection()

    print("Aiven MySQL connection successful!")

    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE()")
    
    result = cursor.fetchone()

    print("Connected database:", result[0])

    cursor.close()
    conn.close()

except Exception as e:
    print("Connection failed!")
    print("Error:", e)
    