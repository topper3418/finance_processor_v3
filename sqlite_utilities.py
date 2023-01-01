import sqlite3
import pandas
import pandas_utilities


class DbSession:

    def __init__(self, filepath):
        self.filepath = filepath
        self.print_indentation_level = 0
        self.print('Opening database file')
        self.connection = sqlite3.connect(filepath)
        self.print_indentation_level = 1
        self.commits = 0
        self.queries = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f'{exc_type=}, {exc_val=}, {exc_tb=}')
        self.print_indentation_level = 0
        self.print(f'Closing database file after {self.queries} queries and {self.commits} commits\n')
        self.connection.close()

    @property
    def tables(self):
        table_data = self.fetch_query("SELECT name FROM sqlite_master WHERE type = 'table'")
        return table_data['name'].tolist()

    def print(self, *args, **kwargs):
        margin = '\t'*self.print_indentation_level
        print(margin, end='')
        print(*args, **kwargs)

    def fetch_query(self, query) -> pandas.DataFrame:
        print(query)
        results = pandas.read_sql_query(query, self.connection)
        self.queries += 1
        return results

    def fetch_single_value(self, query):
        result_table = self.fetch_query(query)
        return result_table.iloc[0, 0]

    def fetch_column(self, query):
        """returns a list from a query that should be structured to return only one row"""
        result_table = self.fetch_query(query)
        return result_table.iloc[:, 0].tolist()

    def commit_query(self, query):
        print(query)
        self.connection.execute(query)
        self.connection.commit()
        self.commits += 1

    def select_all(self, table):
        return self.fetch_query(f"SELECT * FROM {table}")

    def get_table_info(self, table_name):
        if table_name not in self.tables:
            raise Exception(f'{table_name} not a table')
        return self.fetch_query(f"PRAGMA table_info('{table_name}')")



if __name__ == '__main__':
    # Open a connection to the database
    database = 'database.db'
    with DbSession(database) as session:
        print(session.tables)
