import sqlite3
# access trains.db to query
conn = sqlite3.connect('resource/trains.db')
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

# insert train
def insert(train):
    with conn:
        c.execute("INSERT INTO trains (name, start, end) VALUES (?, ?, ?)",
                  (train.name, train.start.strftime('%H:%M'), train.end.strftime('%H:%M')))
        
# update train
def update(train_id, new_name, new_start, new_end):
    with conn:
        c.execute("UPDATE trains SET name = ?, start = ?, end = ? WHERE id = ?",
                  (new_name, new_start.strftime('%H:%M'), new_end.strftime('%H:%M'), train_id))
        
#get train through id train 
def getTrain(train_id):
    with conn:
        c.execute("SELECT * FROM trains WHERE id = ?",(train_id,))
    return c.fetchone()

# list all trains exist in database
def listTrain():
    c.execute("SELECT * FROM trains")
    return c.fetchall()

# remove train through id train
def remove(train_id):
    with conn:
        c.execute("DELETE FROM trains WHERE id = ?", (train_id,))