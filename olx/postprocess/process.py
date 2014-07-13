import sqlite3, sys, atexit

from datetime import datetime

database_connection = None
database_path = None
def get_conn():
    global database_connection, database_path
    if not database_connection:
        database_connection = sqlite3.connect(database_path)
        atexit.register(close_connection)
        database_connection.execute("""
            CREATE TABLE IF NOT EXISTS phonedetails
              ( phone INTEGER,
                chart TEXT,
                CONSTRAINT phone_index UNIQUE (phone) ON CONFLICT REPLACE)
        """)

    return database_connection

def close_connection():
    global database_connection
    if database_connection:
        database_connection.close()
        database_connection = None

def get_all_phone_data():
    conn = get_conn()
    cur = conn.cursor()
    items = cur.execute("""
                            select phone, time, count(*)
                            from items
                            where phone
                            in
                                ( select  phone from items
                                  group by phone
                                  having count(*) > 1 and phone!=0 )
                            group by phone, time
                            order by phone, time
                        """)
    return cur

def insert_phone(details):
    conn = get_conn()
    conn.executemany('INSERT OR REPLACE INTO phonedetails VALUES (? ,?)', details)
    conn.commit()

def process_phone_data(cursor):
    current_phone = None
    chart = None
    while True:
        row = cursor.fetchone()

        if not row:
            if chart:
                yield (current_phone, repr(chart))
            break

        phone = int(row[0])

        if current_phone != phone:
            if chart:
                yield (current_phone, repr(chart))
            chart = []
            current_phone = phone

        time = datetime.fromtimestamp(int(row[1])).date()
        count = int(row[2])
        today = datetime.now().date()

        chart.append( ((today - time).days, count,) )

def main():
    if len(sys.argv) == 1:
        print("olx database path is needed.")
        exit(-1)

    global database_path
    database_path = sys.argv[1]

    insert_phone(process_phone_data(get_all_phone_data()))

if __name__ == "__main__":
    main()