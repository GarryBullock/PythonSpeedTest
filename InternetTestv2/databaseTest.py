import sqlite3 as sql
from datetime import date, datetime

db = sql.connect('data/sqlite3.sqlite')
#db = sql.connect(':memory:')

id = 1
down = 5
up = 10
date = datetime.now()

cursor = db.cursor()
cursor.execute('''CREATE TABLE tweets(id INTEGER PRIMARY KEY, Down_Speed INTEGER,
                  Up_Speed INTEGER, Log_Date DATE)''')
db.commit()

cursor.execute('''INSERT INTO tweets(id, Down_Speed, Up_Speed, Log_Date)
                  VALUES(?,?,?,?)''', (id,down,up,date))
db.commit()

cursor.execute('''SELECT id, Down_Speed, Up_Speed, Log_Date FROM tweets''')
for row in cursor:
    print(row)
db.close()
