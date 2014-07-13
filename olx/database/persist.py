import sqlite3
import atexit
from datetime import datetime

__connection_object = None
__larget_date = None

def __get_connection():
    if not __connection_object:
        __init()

    return __connection_object

def __init():
    global __connection_object
    __connection_object = sqlite3.connect('olx.db')
    atexit.register(close_connection)
    __connection_object.execute('''
        CREATE TABLE IF NOT EXISTS items
          ( url TEXT,
            title TEXT,
            phone INTEGER,
            name TEXT,
            price INTEGER,
            time INTEGER,
            types TEXT,
            desc TEXT,
            image TEXT,
            CONSTRAINT url_index UNIQUE (url, time) ON CONFLICT REPLACE)
        ''')

    __connection_object.execute('''
        CREATE TABLE IF NOT EXISTS current_state
          ( type TEXT,
            value TEXT,
            CONSTRAINT type_index UNIQUE (type) ON CONFLICT REPLACE )
        ''')
    __connection_object.commit()

    global __larget_date
    date = get_date()
    if date:
        __larget_date = int(date.strftime("%s"))

def close_connection():
    global __connection_object
    if __connection_object:
        __connection_object.close()
        __connection_object = None

DATE_TYPE='LAST_DATE'
def update_date(date):
    conn = __get_connection()
    conn.execute('INSERT OR REPLACE INTO current_state VALUES (? ,?)', (DATE_TYPE, date))
    conn.commit()

def get_date():
    conn = __get_connection()
    date = conn.execute('SELECT value FROM current_state where type=?', [DATE_TYPE]).fetchone()
    try:
        if date:
            return datetime.fromtimestamp(int(date[0])).date()
    except ValueError:
        pass

    return None

def get_items_from(date):
    conn = __get_connection()
    items = conn.execute('SELECT url from items where time>=?', [int(date.strftime("%s"))]).fetchall()
    return list(sum(items,()))

def persist_item(item):
    conn = __get_connection()
    date = int(item['time'].strftime("%s"))
    conn.execute('INSERT INTO items VALUES (?,?,?,?,?,?,?,?,?)', (item['url'], item['title'], item['phone'], item['name'], item['price'], date, ','.join(item['types']), item['desc'], ','.join(item['image'])))
    conn.commit()

    global __larget_date
    if not __larget_date or date > __larget_date:
        __larget_date = date

def persist_largest_date():
    global __larget_date
    if __larget_date:
        update_date(__larget_date)


