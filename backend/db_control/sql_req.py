from db.database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("DELETE FROM users;")

conn.commit()
conn.close()
