import os


# prompt user for name (1: travis, 2: emily)
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


# prompt user for filepath to directory
def get_filepath(user):
    filepath = input(f"Hello, {user}.\n"
                     f"\n"
                     f"Please enter the filepath containing\n"
                     f"the files you would like to process\n"
                     f"\n"
                     f"filepath: ")
    if not os.path.isdir(filepath):
        raise Exception('Error, filepath not found')
    print(os.listdir(filepath))


# loop through files, loading into objects
# load all into an "all_raw_table", headers [date, amount, memo, account, person]
# do a first pass, trying to match vendors and types based on memos from DB
# find first (chronological) unknown type or vendor
# prompt user to copy "snippet" to identify vendor
# look vendor up in vendor database [vendor key, vendor id, typical type]
##  if new vendor, ask for type (repeat lookup process), add new vendor
##  if existing vendor, suggest the most common type, allow for override
# add those values to the table

def main():
    user = get_name()
    get_filepath(user)


if __name__ == '__main__':
    main()
