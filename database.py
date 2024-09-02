# database.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect('user_requests.db')
cursor = conn.cursor()

def create_table():
    cursor.execute('CREATE TABLE IF NOT EXISTS user_requests (user_id INTEGER, command TEXT, timestamp TEXT)')

def insert_request(user_id, command, timestamp):
    cursor.execute('INSERT INTO user_requests VALUES (?, ?, ?)', (user_id, command, timestamp))
    conn.commit()

def get_last_requests(user_id, limit=10):
    cursor.execute('SELECT command, timestamp FROM user_requests WHERE user_id=? ORDER BY timestamp DESC LIMIT ?', (user_id, limit))
    return cursor.fetchall()

create_table()
