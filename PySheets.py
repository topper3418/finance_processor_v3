from __future__ import annotations
import csv
from typing import List, Callable, Iterable


class PyTable:
    """Template for working with and manipulating tables. the row formatting allows
    for memory-light accessing of values via the headers. it includes a make_row()
    method that links the data to the headers."""

    # row formatting
    class PyRow(list):

        def __init__(self, row: Iterable, parent: PyTable):
            self.rows = 0
            self.cols = 0
            super().__init__(row)
            self.parent = parent

        def __getitem__(self, item):
            if isinstance(item, str) and item in self.parent.headers:
                item_index = self.parent.headers.index(item)
                return super().__getitem__(item_index)
            return super().__getitem__(item)

        def __setitem__(self, key, value):
            if isinstance(key, str) and key in self.parent.headers:
                key_ind = self.parent.headers.index(key)
                return super().__setitem__(key_ind, value)
            return super().__setitem__(key, value)

        def string_list(self):
            return [str(item) for item in self]

        def print_format(self, widths, sep: str = ' ') -> str:
            string = '|'+sep
            for item, width in zip(self, widths):
                string += f'{str(item).rjust(width, sep)}{sep}|'
            return string

    row_format = PyRow

    def make_row(self, row):
        return self.row_format(row, self)

    # the rest of the class
    def __init__(self, headers: List[str], data: List[list]):
        self.headers = headers
        self.data = data

    @property
    def headers(self) -> row_format:
        return self._headers

    @headers.setter
    def headers(self, value):
        if not isinstance(value, list):
            raise ValueError("The 'headers' attribute must be a list")
        if not all(isinstance(header, str) for header in value):
            raise ValueError("All headers must be strings")
        self._headers = self.make_row(value)

    @property
    def data(self) -> List[row_format]:
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, list):
            raise ValueError("The 'data' attribute must be a list.")
        if not all(isinstance(row, Iterable) for row in value):
            raise ValueError(f"All rows in the 'data' attribute must be Iterable.")
        if len(set(len(row) for row in value)) > 1:
            raise ValueError("All rows in the 'data' attribute must have the same length as each other")
        if len(value) > 0:
            self._data = [self.make_row(row) for row in value]
            self.rows = len(value)
            self.cols = len(value[0])
        else:
            self._data = self.row_format([[None]*self.cols])
            self.rows = 0

    @property
    def cols(self):
        return self._cols

    @cols.setter
    def cols(self, value: int):
        self._cols = value

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value: int):
        self._rows = value

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

    def print(self, num_rows: int = -1) -> None:
        """same as above, but will always have headers"""
        # determine the  width of each column
        widths = []
        for header, column in zip(self.headers, self.get_data_as_columns()):
            width = max([len(str(header))] + [len(str(value)) for value in column])
            widths.append(width)

        blank: str = self.make_row(['']*self.cols).print_format(widths, sep='-')

        # print blank, headers, blank, data, blank
        print(blank)
        print(self.headers.print_format(widths))
        print(blank)
        for ii, row in enumerate(self.data):
            print(row.print_format(widths))
            if num_rows != -1 and ii+1 >= num_rows:
                break
        print(blank)
        
    def filter(self, header, value, drop=False):
        """returns a sheet where the column matches the value"""
        self.data = [row for row in self.data if row[header] == value]
        if drop: self.drop_column(header)

    def sort(self, sort_func: Callable, reverse: bool = False):
        self.data = sorted(self.data, key=sort_func, reverse=reverse)

    def filter_by_func(self, filter_func: Callable):
        self.data = [row for row in self.data if filter_func(row)]

    def get_column_as_list(self, col_index: int | str):
        return [row[col_index] for row in self.data]

    def get_data_as_columns(self) -> List[list]:
        return [self.get_column_as_list(col_index) for col_index in range(self.cols)]

    def columns_to_rows(self, columns: List[list]):
        self.data = [self.row_format(row) for row in zip(*columns)]

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

    def add_column(self, new_header, new_col: list):
        self.headers.append(new_header)
        self.data = [row + [item] for item, row in zip(new_col, self.data)]

    def generate_list(self, generating_func: Callable) -> list:
        """this function generates a list from the data using a generating function. This function should take in
        a row of data and return a value from it"""
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
        # run the function
        list_out = []
        for row in self.data:
            for category, excerpts in lookup.items():
                if not exact_match and \
                        any(excerpt.upper() in row[header].upper() for excerpt in excerpts):
                    list_out.append(category)
                    break
                elif exact_match and \
                        any(excerpt == row[header] for excerpt in excerpts):
                    list_out.append(category)
                    break
            else:
                list_out.append('UNKNOWN')
        return list_out

    def select_columns(self, new_headers: List[str]):
        """takes in a list of headers and rearranges the data accordingly. all items in the list must
        match current headers, although not all headers need be included. Missing headers will be dropped"""
        # first make sure all headers are in self.headers
        if any(header not in self.headers for header in new_headers):
            raise IndexError(f'headers: {new_headers} are not all in self.headers')
        # make an empty data array, loop through data adding rows to that data that match the order
        new_data = []
        new_header_indices = [self.get_index(header) for header in new_headers]
        for row in self.data:
            new_data.append([row[index] for index in new_header_indices])
        # change headers and data
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
        # loop through the list and get the sums
        for row in self.data:
            category = row[pivot_header]
            value = row[value_header]
            categories_dict[category] += float(value)
        # create the table
        pivot_data = [[category, round(value, 2)] for category, value in categories_dict.items()]
        pivot_table = PyTable([pivot_header, value_header], pivot_data)
        pivot_table.sort(lambda row: row[1], reverse=True)
        return pivot_table

    def format_col(self, header, format_func):
        """runs the format func on every item in the given column"""
        for row in self.data:
            row[header] = format_func(row[header])

    def __add__(self, other: PyTable) -> PyTable:
        """returns a table with the second appended to the first"""
        # make sure the other table is in fact a PyTable
        if not isinstance(other, PyTable):
            raise TypeError(f'Second type is not a pyTable. it is a {type(other)}')
        # make sure headers are consistent. Only requirement is first headers are all present in second
        if not all(header in self.headers for header in other.headers):
            raise Exception("Not all of second table's headers are in the first table's headers")
        # add the data
        return PyTable(self.headers, self.data + other.data)

# TODO make classes for significant data types. This includes the raw format
# marked on each 'get' function, but also for the bigger tables and pivots.
# the raw one should include a connection some sqlite stuff.


def from_csv(filepath) -> List[list]:
    # make sure it is a csv file
    if filepath[-4:] != '.csv':
        raise Exception(f'{filepath} is not a .csv')
    # get all the rows from the file
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    # make data
    return data


def main():
    sheet = from_csv('/Users/travisopperud/Documents/GitHub/finance_processor_v3/Data/'
                     'Emily/Chase6251_Activity20220801_20221212_20221212.csv'
    )
    table = PyTable(sheet[0], sheet[1:])
    table.select_columns(['Transaction Date', 'Description', 'Amount'])
    table.headers = ['Date', 'Memo', 'Amount']
    table.print(num_rows=20)


if __name__ == '__main__':
    main()
