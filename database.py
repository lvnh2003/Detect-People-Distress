import sqlite3

conn = sqlite3.connect('trains.db')
c = conn.cursor()

create_table_query = '''
    CREATE TABLE IF NOT EXISTS trains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        start TEXT,
        end TEXT
    )
'''
c.execute(create_table_query)
conn.commit()

class Train:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

def insert(train):
    with conn:
        c.execute("INSERT INTO trains (name, start, end) VALUES (?, ?, ?)",
                  (train.name, train.start.strftime('%H:%M'), train.end.strftime('%H:%M')))
def update(train_id, new_name, new_start, new_end):
    with conn:
        c.execute("UPDATE trains SET name = ?, start = ?, end = ? WHERE id = ?",
                  (new_name, new_start.strftime('%H:%M'), new_end.strftime('%H:%M'), train_id))
def getTrain(train_id):
    with conn:
        c.execute("SELECT * FROM trains WHERE id = ?",(train_id,))
    return c.fetchone()
def listTrain():
    c.execute("SELECT * FROM trains")
    return c.fetchall()
def remove(train_id):
    with conn:
        c.execute("DELETE FROM trains WHERE id = ?", (train_id,))