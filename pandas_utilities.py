from __future__ import annotations
from typing import List, Callable, Iterable

import csv
import pandas
import sqlite3


class PyTable(pandas.DataFrame):
        
    pass

# TODO make classes for significant raw_data types
# marked on each 'get' function, but also for the bigger tables and pivots.
# the raw one should include a connection some sqlite stuff.


class StrippedCsv(PyTable):

    headers = ['Date', 'Memo', 'Amount', 'Source_file', 'Person']

    def __init__(self, data: List[list] = None):
        if data is None:
            data = [self.row_format([None]*self.cols)]
        self.data = data


class HeadlessData(PyTable):

    def __init__(self, data: List[list]):
        self.data = data

    @property
    def cols(self):
        return len(self.data[0])

    @property
    def headers(self):
        return list(range(self.cols))

    def print(self, num_rows: int = -1, indents: int = 0):
        return super().print(num_rows=num_rows, indents=indents, print_headers=False)


def from_csv(filepath):
    # make sure it is a csv file
    if filepath[-4:] != '.csv':
        raise Exception(f'{filepath} is not a .csv')
    # get all the rows from the file
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    # make raw_data
    return data


def to_csv(data, filepath):
    # make sure it is a csv file
    if filepath[-4:] != '.csv':
        raise Exception(f'{filepath} is not a .csv')
    # write the raw_data to the file
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


class SqliteTable(PyTable):
    """this is meant to be a table that has a corresponding table in a database. when manipulated, that table will
    also change"""

    def __init__(self, filepath: str, table_name: str):
        self.filepath = filepath
        self.table_name = table_name
        if not self.validate_table_name():
            raise Exception(f"{table_name} is not a valid table name in the database")

    def validate_table_name(self):
        with DbSession(filepath=self.filepath) as conn:
            valid_tables = conn.tables
            return self.table_name in valid_tables


def csv_example():
    sheet = from_csv(
        'C:\\Users\\Travis\\Documents\\GitHub\\finance_processor_v3\\'
        'Data\\Travis\\Chase4452_Activity20220801_20221211_20221212.csv'
    )
    table = PyTable(sheet[0], sheet[1:])
    table.select_columns(['Transaction Date', 'Description', 'Amount'])
    table.headers = ['Date', 'Memo', 'Amount']
    table.print(num_rows=20)


def main():
    pass


if __name__ == '__main__':
    main()
