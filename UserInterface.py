import os
from typing import Dict, List
from PySheets import from_csv


def get_name():
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


def main():
    # prompt user for name (1: travis, 2: emily)
    user = get_name()
    # prompt user for filepath to directory
    filepath = get_filepaths(user)
    # loop through files, loading into objects
    raw_data = get_raw_objects(filepath)
    # load all into an "all_raw_table", headers [date, amount, memo, account, person]
    # do a first pass, trying to match vendors and types based on memos from DB
    # find first (chronological) unknown type or vendor
    # prompt user to copy "snippet" to identify vendor
    # look vendor up in vendor database [vendor key, vendor id, typical type]
    ##  if new vendor, ask for type (repeat lookup process), add new vendor
    ##  if existing vendor, suggest the most common type, allow for override
    # add those values to the table


if __name__ == '__main__':
    main()
