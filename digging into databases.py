import sqlite3
import pandas

database_filepath = input('database filepath:'
                          '> ')

with sqlite3.connect(database_filepath) as conn:
    user_input = ''
    while user_input.upper() != 'EXIT':
        user_input = input('\n\nnew query:\n')
        if user_input.upper() not in ('', 'EXIT', 'COMMIT'):
            try:
                results = pandas.read_sql_query(user_input, conn)
                print(results.to_string())
            except TypeError as err:
                print(f"WARNING: '{err}' thrown, ignore if you entered an update query")
        if user_input.upper() == 'COMMIT':
            conn.commit()



