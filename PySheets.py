from __future__ import annotations
import csv
from typing import List, Callable, Iterable
import sqlite3


class PyTable:

    class PyRowFormat(list):

        def __init__(self, list_in, parent: PyTable):
            super().__init__(list_in)
            self.parent = parent

        def string_list(self):
            return [str(item) for item in self]

        def __getitem__(self, item):
            if isinstance(item, str) and item in self.parent.headers:
                ind = self.parent.headers.index(item)
                return super().__getitem__(ind)
            if isinstance(item, int):
                return super().__getitem__(item)

        def __eq__(self, other):
            if type(other) != type(self):
                raise TypeError(f'Expected {type(self)}, got {type(other)}')
            return all([self_item == other_item
                        for self_item, other_item
                        in zip(self, other)])

    row_format = PyRowFormat

    def __init__(self, headers: List[str], data: List[list]):
        self.headers = headers
        self.data = data

    @property
    def headers(self) -> List[str]:
        return self._headers

    @headers.setter
    def headers(self, value):
        if not isinstance(value, list):
            raise ValueError("The 'headers' attribute must be a list")
        if not all(isinstance(header, str) for header in value):
            raise ValueError("All headers must be strings")
        self._headers = self.row_format(value, self)

    @property
    def data(self) -> List[row_format]:
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, list):
            raise ValueError("The 'raw_data' attribute must be a list.")
        if not all(isinstance(row, Iterable) for row in value):
            raise ValueError("All rows in the 'raw_data' attribute must be lists.")
        if len(set(len(row) for row in value)) > 1:
            raise ValueError("All rows in the 'raw_data' attribute must have the same length as each other")
        if len(value) > 0:
            self._data = [self.row_format(row, self) for row in value]
        else:
            self._data = [self.row_format([[None]*self.cols], self)]

    @property
    def cols(self) -> int:
        return len(self.headers)

    @property
    def rows(self):
        return len(self.data) if self.has_data else 0

    @property
    def has_data(self):
        return len(self.data) > 1 or self[0] != self.row_format([None]*self.cols)

    def get_index(self, header) -> int:
        """basically this will take in a header (or an int) and return an int. if input is an int
        then it will return the int. if it is a string that is in headers, it will return the index
        of that header"""
        if isinstance(header, int):
            return header
        if header in self.headers:
            return self.headers.index(header)
        else:
            raise IndexError(f'{header} is not a valid column index for this table')

    def get_widths(self):
        widths = []
        for header, column in zip(self.headers, self.get_data_as_columns()):
            width = max([len(str(header))] +[len(str(value)) for value in column])
            widths.append(width)
        return widths

    def print(self, num_rows: int = -1, indents: int = 0, print_headers: bool = True) -> None:
        """same as above, but will always have headers"""
        # determine the  width of each column
        margin = '\t'*indents

        widths = self.get_widths()

        def print_blank():
            line = margin + '+'
            for width in widths:
                line += '-' * width + '--+'
            print(line)

        # define the function for printing out a full row
        def print_line(row_in):
            line = margin + '|'
            for width, item in zip(widths, row_in):
                line += f" {str(item).rjust(width)} |"
            print(line)

        # print blank, headers, blank, raw_data, blank
        if print_headers:
            print_blank()
            print_line(self.headers)
        print_blank()
        for ii, row in enumerate(self.data):
            print_line(row)
            if num_rows != -1 and ii+1 >= num_rows:
                break
        print_blank()
        
    def filter(self, header, value, drop=False):
        """returns a sheet where the column matches the value"""
        self.data = [row for row in self.data if row[header] == value]
        if drop: self.drop_column(header)

    def sort(self, sort_func: Callable, reverse: bool = False):
        self.data = sorted(self.data, key=sort_func, reverse=reverse)

    def filter_by_func(self, filter_func: Callable):
        self.data = [row for row in self.data if filter_func(row)]

    def get_column_as_list(self, col_index: int | str):
        col_index = self.get_index(col_index)
        return [row[col_index] for row in self.data]

    def get_data_as_columns(self) -> List[list]:
        return [self.get_column_as_list(col_index) for col_index in range(self.cols)]

    def columns_to_rows(self, columns: List[list]):
        self.data = [list(row) for row in zip(*columns)]

    def drop_column(self, index_in: int | str):
        """Drops a column at a given index"""
        # convert to a single list if necessary
        columns = self.get_data_as_columns()
        index_in = self.get_index(index_in)
        columns.pop(index_in)
        self.columns_to_rows(columns)

    def drop_columns(self, indices: List[int | str]):
        """like drop_column, but put in a list of columns to drop"""
        for index in indices:
            self.drop_column(index)

    def add_column(self, new_header, new_col):
        self.headers.append(new_header)
        if isinstance(new_col, list):
            self.data = [row + [item] for item, row in zip(new_col, self.data)]
        if not isinstance(new_col, Iterable):
            self.data = [row + [new_col] for row in self.data]
        self.data = [row + [new_col] for row in self]

    def generate_list(self, generating_func: Callable) -> list:
        """this function generates a list from the raw_data using a generating function. This function should take in
        a row of raw_data and return a value from it"""
        return [generating_func(row) for row in self.data]

    def generate_column(self, new_header, generating_func: Callable) -> None:
        """this function adds a column to the end of the sheet. The generating function should take in a row and
        return a single value"""
        self.headers.append(new_header)
        # use the generate_list method
        new_column = self.generate_list(generating_func)
        # use the add_column method
        self.add_column(new_column)

    def generate_list_from_lookup(self, header: str, lookup: dict, exact_match: bool = False):
        """This function works like generate list, but it does it with a lookup in order to
        generate that list."""
        # get header index
        header_ind = self.get_index(header)
        # run the function
        list_out = []
        for row in self.data:
            for category, excerpts in lookup.items():
                if not exact_match and \
                        any(excerpt.upper() in row[header_ind].upper() for excerpt in excerpts):
                    list_out.append(category)
                    break
                elif exact_match and \
                        any(excerpt == row[header_ind] for excerpt in excerpts):
                    list_out.append(category)
                    break
            else:
                list_out.append('UNKNOWN')
        return list_out

    def select_columns(self, new_headers: List[str]):
        """takes in a list of headers and rearranges the raw_data accordingly. all items in the list must
        match current headers, although not all headers need be included. Missing headers will be dropped"""
        # first make sure all headers are in self.headers
        if any(header not in self.headers for header in new_headers):
            raise IndexError(f'headers: {new_headers} are not all in self.headers')
        # make an empty raw_data array, loop through raw_data adding rows to that raw_data that match the order
        new_data = []
        new_header_indices = [self.get_index(header) for header in new_headers]
        for row in self.data:
            new_data.append([row[index] for index in new_header_indices])
        # change headers and raw_data
        self.data = new_data
        self.headers = new_headers

    def pivot(self, pivot_header, value_header) -> PyTable:
        """pivots on a row. gets each unique value in the pivot row, and sums the value
        header for each"""
        # make sure both headers are valid
        if not pivot_header in self.headers:
            raise Exception(f'{pivot_header} not in headers')
        if not value_header in self.headers:
            raise Exception(f'{value_header} not in headers')
        # get unique values for the header
        categories = set(self.get_column_as_list(pivot_header))
        categories_dict = {category: 0 for category in categories}
        pivot_ind = self.get_index(pivot_header)
        value_ind = self.get_index(value_header)
        # loop through the list and get the sums
        for row in self.data:
            category = row[pivot_ind]
            value = row[value_ind]
            categories_dict[category] += float(value)
        # create the table
        pivot_data = [[category, round(value, 2)] for category, value in categories_dict.items()]
        pivot_table = PyTable([pivot_header, value_header], pivot_data)
        pivot_table.sort(lambda row: row[1], reverse=True)
        return pivot_table

    def format_col(self, header, format_func):
        """runs the format func on every item in the given column"""
        header_ind = self.get_index(header)
        for row in self.data:
            row[header_ind] = format_func(row[header_ind])

    def to_PyTable(self):
        """meant for subclasses, a way to turn them back to general tables"""
        return PyTable(self.headers, self.data)

    def to_csv(self, filepath):
        all_data = [self.headers] + self.data
        to_csv(all_data, filepath)

    def __add__(self, other: PyTable) -> PyTable:
        """returns a table with the second appended to the first"""
        # make sure the other table is in fact a PyTable
        if not isinstance(other, PyTable):
            raise TypeError(f'Second type is not a pyTable. it is a {type(other)}')
        # make sure headers are consistent. Only requirement is first headers are all present in second
        if not all(header in self.headers for header in other.headers):
            raise Exception("Not all of second table's headers are in the first table's headers")
        if not all(header == other_header for header, other_header in zip(self.headers, other.headers)):
            other.select_columns(self.headers)
        # add the raw_data
        return PyTable(self.headers, self.data + other.data)

    def __iadd__(self, other):
        """appends the other table's raw_data to self.raw_data"""
        # make sure the other table is in fact a PyTable
        if not isinstance(other, PyTable):
            raise TypeError(f'Second type is not a pyTable. it is a {type(other)}')
        # make sure headers are consistent. Only requirement is first headers are all present in second
        if not all(header in self.headers for header in other.headers):
            raise Exception("Not all of second table's headers are in the first table's headers")
        if not all(header == other_header for header, other_header in zip(self.headers, other.headers)):
            other.select_columns(self.headers)
        self.data.extend(other.data)
        return self

    def __iter__(self):
        for row in self.data:
            yield row

    def __getitem__(self, item):
        return self.data[item]

    def __repr__(self):
        return f"{type(self)} with {self.rows} rows and {self.cols} columns"

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
        return [row[0] for row in table_data]

    def print(self, *args, **kwargs):
        margin = '\t'*self.print_indentation_level
        print(margin, end='')
        print(*args, **kwargs)

    def fetch_query(self, query) -> PyTable:
        cursor = self.connection.execute(query)
        headers = [row[0] for row in cursor.description]
        self.queries += 1
        return PyTable(headers, cursor.fetchall())

    def fetch_single_value(self, query):
        result_table = self.fetch_query(query)
        return result_table[0][0]

    def commit_query(self, query):
        self.connection.execute(query)
        self.connection.commit()
        self.commits += 1

    def select_all(self, table):
        return self.fetch_query(f"SELECT * FROM {table}")

    def get_table_info(self, table_name):
        if table_name not in self.tables:
            raise Exception(f'{table_name} not a table')
        table_info = self.fetch_query(f"PRAGMA table_info('{table_name}')")
        self.print(f'{table_name} info')
        table_info.print(indents=self.print_indentation_level)


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
