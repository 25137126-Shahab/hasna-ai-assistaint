import sqlite3

conn = sqlite3.connect("hansa.db")
cursor = conn.cursor()

# Database initialization code
# Uncomment to create tables
# query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
# cursor.execute(query)
# query = "INSERT INTO sys_command VALUES (null,'OneNote', 'C:\\Program Files\\Microsoft Office\\root\\Office16\\ONENOTE.exe')"
# cursor.execute(query)
# conn.commit()