import os
from typing import Dict, List
from PySheets import from_csv, StrippedCsv, PyTable, HeadlessData
from sqlite_utilities import FinanceDbSession
import sqlite3

from main import check_lookup


def get_name() -> str:
    name_ind = input('Available profiles:\n'
                     '1) Travis\n'
                     '2) Emily\n'
                     '\n'
                     '(1/2): ')
    if name_ind not in ['1', '2']:
        raise IndexError(f'Only 1 and 2 can be inputs, you entered {name_ind}')
    print('\n\n')
    return ['Travis', 'Emily'][int(name_ind) - 1]


def get_filepaths(user):
    filepath = input(f"Hello, {user}.\n"
                     f"\n"
                     f"Please enter the filepath containing\n"
                     f"the files you would like to process\n"
                     f"\n"
                     f"filepath: ")
    if not os.path.isdir(filepath):
        raise Exception('Error, filepath not found')
    if not any(file.endswith('.csv') for file in os.listdir(filepath)):
        raise Exception('Error, no csv files found in directory')
    print('\n\n\n')
    return filepath


def get_raw_objects(filepath):
    os.chdir(filepath)
    dict_out: Dict[str: List[list]] = {}
    for file in os.listdir(filepath):
        if not file.endswith('.csv'):
            print(f'skipping {file}')
            continue
        print(f'loading {file}')
        dict_out[file] = from_csv(file)
    return dict_out


def get_chase_table(data) -> PyTable:
    table = PyTable(data[0], data[1:])
    table.select_columns(['Transaction Date', 'Description', 'Amount'])
    table.headers = ['Date', 'Memo', 'Amount']
    return table


def get_wells_table(data) -> PyTable:
    table = PyTable(['Date', 'Amount', 'Stars', 'Blanks', 'Memo'], data)
    table.select_columns(['Date', 'Memo', 'Amount'])
    return table


def get_apple_table(data) -> PyTable:
    table = PyTable(data[0], data[1:])
    table.select_columns(['Transaction Date', 'Description', 'Amount (USD)'])
    table.headers = ['Date', 'Memo', 'Amount']
    return table


def make_StrippedCsv(table: PyTable, filename, user):
    table.add_column('Source_file', filename)
    table.add_column('Person', user)
    return StrippedCsv(table.data)


def main():
    # prompt user for name (1: travis, 2: emily)
    user = get_name()

    # prompt user for filepath to directory
    filepath = get_filepaths(user)
    # loop through files, loading into objects
    raw_data = get_raw_objects(filepath)

    filename_lookup = {
        get_chase_table: ['Chase'],
        get_wells_table: ['Checking',
                          'PreferredChecking',
                          'Savings'],
        get_apple_table: ['Apple']
    }
    # make a blank table with static headers
    all_table = StrippedCsv()
    # load all into an "all_raw_table", headers [date, amount, memo, account, person]
    for filename, data in raw_data.items():
        parsing_func = check_lookup(filename, filename_lookup,
                                    missing_function=lambda a: print(f'No parsing function made for '
                                                                     f'filenames like {a} yet'))
        if parsing_func is None:
            continue

        print(f'parsing {filename}......'.ljust(90, '.'), end='')
        table = parsing_func(data)
        all_table += make_StrippedCsv(table, filename, user)
        print(f'success')
    print('\n\n\n\n\n')
    all_table.print(125)
    # now for sqlite implementation
    database = 'finance.db'
    try:
        conn = FinanceDbSession(database)
        c = conn.cursor()
        c.fetch_query('SELECT * FROM vendors')
        for row in c.descript
    except sqlite3.Error as error:
        print('Failed to check tables', error)

    finally:
        if conn:
            # using close() method, we will close
            # the connection
            conn.close()

            # After closing connection object, we
            # will print "the sqlite connection is
            # closed"
            print("the sqlite connection is closed")
    # do a first pass, trying to match vendors and types based on memos from DB
    # loop through the table
    # look through all recorded snippets to populate suggested vendor and type
    # find first (chronological) unknown type or vendor
    # can also access a PK-correlated list of exceptions
    # prompt user to copy "snippet" to identify
    # show all items in dataset this applis to
    # look vendor up in vendor database [vendor key, vendor id, typical type
    # add those values to the table


if __name__ == '__main__':
    main()
