import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("college.db")
cursor = conn.cursor()

# Institution Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS institutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    city TEXT,
    type TEXT
)
""")

# Admin Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Default Admin
username = "admin"
password = generate_password_hash("Admin@123")

cursor.execute("SELECT * FROM admin WHERE username=?", (username,))
admin = cursor.fetchone()

if not admin:
    cursor.execute(
        "INSERT INTO admin(username,password) VALUES(?,?)",
        (username, password)
    )

conn.commit()
conn.close()

print("Database Ready Successfully!")