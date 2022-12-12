from __future__ import annotations
import csv
from typing import List, Callable


class PySheet:

    def __init__(self, filepath):
        # make sure it is a csv file
        if filepath[-4:] != '.csv':
            raise Exception('filepath is not of type .csv')
        # get all the rows from the file
        with open(filepath, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
        # make data
        self.data: List[list] = data

    @property
    def data(self) -> List[list]:
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, list):
            raise ValueError("The 'data' attribute must be a list.")
        if not all(isinstance(row, list) for row in value):
            raise ValueError("All rows in the 'data' attribute must be lists.")
        if len(set(len(row) for row in value)) > 1:
            raise ValueError("All rows in the 'data' attribute must have the same length.")
        if len(value) > 0:
            self._data = value
            self.rows = len(value)
            self.cols = len(value[0])
        else:
            self._data = [[None]*self.cols]
            self.rows = 0

    @property
    def cols(self):
        return self._cols

    @cols.setter
    def cols(self, value):
        if not isinstance(value, int):
            raise TypeError('cols must be of type int')
        self._cols = value

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        if not isinstance(value, int):
            raise TypeError('rows must be of type int')
        self._rows = value

    def print(self, num_rows: int = -1, headless: bool = True):
        """this function prints out the data in a nice readable table"""
        # determine the  width of each column
        widths = [max(
                [len(str(value)) for value in column]
            )
                  for column in self.get_data_as_columns()
        ]
        def print_blank():
            line = '+'
            for width in widths:
                line += '-' * width + '--+'
            print(line)

        # define the function for printing out a full row
        def print_line(row_in):
            line = '|'
            for width, item in zip(widths, row_in):
                line += f" {str(item).rjust(width)} |"
            print(line)

        # print blank, headers, blank, data, blank
        print_blank()
        for ii, row in enumerate(self.data):
            print_line(row)
            if ii == 0 and not headless:
                print_blank()
            if num_rows != -1 and ii+1 >= num_rows:
                break
        print_blank()
        
    def filter(self, header, value, drop=False):
        """returns a sheet where the column matches the value"""
        self.data = [row for row in self.data if row[header] == value]
        if drop: self.drop_column(header)

    def filter_by_func(self, filter_func: Callable):
        self.data = [row for row in self.data if filter_func(row)]

    def py_table(self, headers: List[str] = []) -> PyTable:
        if headers: return PyTable(headers, self.data)
        return PyTable(self.data[0], self.data[1:])

    def get_column_as_list(self, col_index: int):
        return [row[col_index] for row in self.data]

    def get_data_as_columns(self) -> List[list]:
        return [self.get_column_as_list(col_index) for col_index in range(self.cols)]

    def columns_to_rows(self, columns: List[list]):
        self.data = [list(row) for row in zip(*columns)]

    def drop_column(self, index_in: int):
        """Drops a column at a given index"""
        # convert to a single list if necessary
        columns = self.get_data_as_columns()
        columns.pop(index_in)
        self.columns_to_rows(columns)

    def drop_columns(self, indices: List[int]):
        """like drop_column, but put in a list of columns to drop"""
        for index in indices:
            self.drop_column(index)

    def add_column(self, new_col: list):
        self.data = [row + [item] for item, row in zip(new_col, self.data)]

    def generate_list(self, generating_func: Callable) -> list:
        """this function generates a list from the data using a generating function. This function should take in
        a row of data and return a value from it"""
        return [generating_func(row) for row in self.data]

    def generate_column(self, generating_func: Callable) -> None:
        """this function adds a column to the end of the sheet. The generating function should take in a row and
        return a single value"""
        # use the generate_list method
        new_column = self.generate_list(generating_func)
        # use the add_column method
        self.add_column(new_column)


class PyTable(PySheet):
    """This will be like a PySheet, except it will have headers and data and such"""

    def __init__(self, headers, data):
        self.data = data
        self.headers = headers

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

    def get_column_as_list(self, index_in: int | str):
        """same as the parent classes method, except can also take a header"""
        int_index = self.get_index(index_in)
        return super(PyTable, self).get_column_as_list(int_index)

    def drop_column(self, index_in: int | str):
        """same as parent method, but can take a header as input"""
        int_index = self.get_index(index_in)
        self.headers.pop(int_index)
        super(PyTable, self).drop_column(int_index)
        
    def add_column(self, new_header: str, new_col: list):
        # new column must be same length as data
        if len(new_col) != self.rows:
            raise Exception('New column is not consistent with data. '
                            f'Expected {self.rows} but got {len(new_col)=}')
        self.headers += [new_header]
        new_header_ind = self.get_index(new_header)
        for row, new_value in zip(self.data, new_col):
            row[new_header_ind] = new_value

    def print(self, num_rows: int = -1) -> None:
        """same as above, but will always have headers"""
        # determine the  width of each column
        widths = []
        for header, column in zip(self.headers, self.get_data_as_columns()):
            width = max([len(str(header))] +[len(str(value)) for value in column])
            widths.append(width)

        def print_blank():
            line = '+'
            for width in widths:
                line += '-' * width + '--+'
            print(line)

        # define the function for printing out a full row
        def print_line(row_in):
            line = '|'
            for width, item in zip(widths, row_in):
                line += f" {str(item).rjust(width)} |"
            print(line)

        # print blank, headers, blank, data, blank
        print_blank()
        print_line(self.headers)
        print_blank()
        for ii, row in enumerate(self.data):
            print_line(row)
            if num_rows != -1 and ii+1 >= num_rows:
                break
        print_blank()

    def filter(self, header, value, drop=False):
        header_ind = self.get_index(header)
        super(PyTable, self).filter(header_ind, value, drop)

    def drop_columns(self, indices: List[str | int]):
        for index in indices:
            self.drop_column(index)

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
        pivot_ind = self.get_index(pivot_header)
        value_ind = self.get_index(value_header)
        # loop through the list and get the sums
        for row in self.data:
            category = row[pivot_ind]
            value = row[value_ind]
            categories_dict[category] += float(value)
        # create the table
        pivot_data = [[category, round(value, 2)] for category, value in categories_dict.items()]
        return PyTable([pivot_header, value_header], pivot_data)

    def format_col(self, header, format_func):
        """runs the format func on every item in the given column"""
        header_ind = self.get_index(header)
        for row in self.data:
            row[header_ind] = format_func(row[header_ind])

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

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value: list):
        if not isinstance(value, list):
            raise TypeError('headers must be of type list')
        if len(value) < self.cols:
            raise Exception(f'headers are inconsistent with data. Expected {self.cols} items but got'
                            f' {len(value)} items')
        elif len(value) == self.cols:
            self._headers = value
        elif len(value) > self.cols:
            self._headers = value
            diff = len(value) - self.cols
            self.data = [row + [None]*diff for row in self.data]


def main():
    sheet = PySheet('C:\\Users\\Travis\\PycharmProjects\\finance_processor_v2\\Data\\Raw\\2021\\Chase.csv')
    table = sheet.py_table()
    table.drop_columns(['Post Date', 'Category', 'Type', 'Memo'])
    table.print(num_rows=20)


if __name__ == '__main__':
    main()
