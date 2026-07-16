import sqlite3

conn = sqlite3.connect("characters.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS characters(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER
        )
        """)

cursor.execute("""
INSERT INTO characters(name, age)
VALUES("REN", 25)
""")

cursor.execute("""
INSERT INTO characters(name, age)
VALUES("Nyra", 23)
""")

cursor.execute("""
INSERT INTO characters(name, age)
VALUES("Sagar", 29)
""")

cursor.execute("""
INSERT INTO characters(name, age)
VALUES("Brook", 30)
""")

cursor.execute("""
INSERT INTO characters(name, age)
VALUES("Kai", 18)
""")

cursor.execute("""
INSERT INTO characters(name, age)
VALUES("Rick", 45)
""")

conn.commit()

cursor.execute("""
SELECT *
FROM characters
""")

rows = cursor.fetchall()

print(rows)
