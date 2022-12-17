import sqlite3
from PySheets import PyTable, HeadlessData

def create_table(conn):
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")


def select_all(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    return c.fetchall()

def check_tables(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS vendors (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name VARCHAR(255),
                      typical_type VARCHAR(255)
                    );
    """)
    conn.commit()
    c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    print('\tTables:')
    table_data = HeadlessData(c.fetchall())
    table_data.print(indents=1)



if __name__ == '__main__':
    # Open a connection to the database
    try:
        conn = sqlite3.connect("database.db")
        check_tables(conn)

        # Create the table
        #create_table(conn)

        # Insert some data into the table
        #conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Alice", 25))
        #conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Bob", 30))
        #conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Eve", 35))
        #conn.commit()

        # Select all rows from the table
        #rows = select_all(conn)

        # Print the rows
        #for row in rows:
        #    print(row)

        # Close the connection
        #conn.close()

    except sqlite3.Error as error:
        print("failed to run properly", error)

    finally:
        if conn:
            # using close() method, we will close
            # the connection
            conn.close()

            # After closing connection object, we
            # will print "the sqlite connection is
            # closed"
            print("the sqlite connection is closed")