from typing import Callable, List, Any, Dict
import os
import pandas
from pandas_utilities import PyTable
from sqlite_utilities import DbSession


class Menu:
    """class that when initialized, prompts user for input. It will then return """

    @classmethod
    def deploy(cls,
               title: str,
               choices: List[str],
               zero_choice: str = '',
               keys: List[Any] = [],
               return_choice: bool = False):
        menu = Menu(title, choices, zero_choice, keys, return_choice)
        return menu.prompt()

    def __init__(self,
                 title: str,
                 choices: List[str],
                 zero_choice: str = '',
                 keys: List[Any] = [],
                 return_choice: bool = False):
        self.title = title
        self.choices = choices
        self.zero_choice = zero_choice
        self.num_choices = len(choices) + int(bool(len(zero_choice)))
        self.return_choice = return_choice
        # if there is manual input for keys
        if keys:
            # and if the keys don't line up with choices
            if len(keys) != self.num_choices:
                raise Exception('Error the number of keys is not consistent with choices')
        self.keys = keys

    def print(self):
        """prints out the menu items in an orderly fashion"""
        print(self.title)
        print()
        for ii, choice in enumerate(self.choices):
            print(f'{ii+1}: {choice}')
        if self.zero_choice:
            print(f'0: {self.zero_choice}\n')

    def prompt(self) -> Any:
        """prompts user to make a choice in the menu"""
        self.print()
        selection = int(input())
        if self.keys and selection in range(len(self.keys)):
            return self.keys[selection]
        if selection > self.num_choices:
            raise Exception('selection out of range')
        if self.return_choice:
            if selection == 0:
                return self.zero_choice
            return self.choices[selection-1]
        return selection


def get_session() -> None:
    """navigates us into an environment where we have a consistent directory tree to work with"""
    # navigate to the "sessions" directory
    os.chdir('sessions')
    # this is where all the sessions are saved
    saved_sessions = os.listdir()
    session = Menu.deploy(
        title='Choose a session:',
        choices=saved_sessions,
        zero_choice='new session',
        return_choice=True
    )
    print(f'you chose {session}')
    if session == 'new session':
        create_new_session()
    else:
        os.chdir(session)


def get_account_data(account_key: str) -> list:
    query = f"""
        SELECT * FROM accounts
        WHERE account_key = `{account_key}`
    """
    with DbSession('database.db') as conn:
        account_data = conn.fetch_query(query)
    return account_data


def create_new_session() -> None:
    """works with the user to create a new session"""
    # first get the name for the new session
    new_session_name = input('New session name: ')
    # make sure it's not already a session
    if new_session_name in os.listdir():
        print('already a session, try again')
        create_new_session()
    # create the folder
    os.mkdir(new_session_name)
    os.chdir(new_session_name)
    # create the database
    initialize_db()
    # create the raw raw_data folder
    os.mkdir('raw_data')
    # create the processed raw_data folder
    os.mkdir('processed_data')


def initialize_db() -> None:
    """static function, creates a predefined database schema"""
    # create the database
    with DbSession('persistent_data.db') as conn:
        # create the type table, for providing a lookup table
        create_type_table = """
            CREATE TABLE IF NOT EXISTS 
                types (
                    type_key    INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_id     VARCHAR(255)
                );
        """
        conn.commit_query(create_type_table)
        # create the vendor table, for correlating to types and providing a lookup
        create_vendor_table = """
            CREATE TABLE IF NOT EXISTS 
                vendors (
                    vendor_key              INTEGER PRIMARY KEY AUTOINCREMENT,
                    vendor_id               VARCHAR(255),
                    is_internal_account     INTEGER(1),
                    typical_type_key        INTEGER,
                    FOREIGN KEY (typical_type_key) REFERENCES types(type_key)
                );
        """
        conn.commit_query(create_vendor_table)
        # create the accounts table, for providing parsing information
        create_accounts_table = """
            CREATE TABLE IF NOT EXISTS 
                accounts (
                    account_key         INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id          VARCHAR(45),
                    date_column         VARCHAR(45),
                    memo_column         VARCHAR(45),
                    amount_column       VARCHAR(45),
                    vendor_key          INTEGER,
                    FOREIGN KEY (vendor_key) REFERENCES vendors(vendor_key)
                );
        """
        conn.commit_query(create_accounts_table)
        # create the snippets table, for auto-labeling the raw_data initially
        # if source account key is the only key not null then its for the filename
        create_snippets_table = """
            CREATE TABLE IF NOT EXISTS 
                snippets (
                    snippet_key         INTEGER PRIMARY KEY AUTOINCREMENT,
                    snippet             VARCHAR(75),
                    source_account_key  INTEGER,
                    type_key            INTEGER,
                    vendor_key          INTEGER,
                    FOREIGN KEY (source_account_key) REFERENCES accounts(accounts_key),
                    FOREIGN KEY (type_key) REFERENCES types(type_key),
                    FOREIGN KEY (vendor_key) REFERENCES vendors(vendor_key)
                );
        """
        conn.commit_query(create_snippets_table)
        # create the transactions table, for adding transactions
        create_transactions_table = """
            CREATE TABLE IF NOT EXISTS 
                transactions (
                    transaction_key     INTEGER PRIMARY KEY AUTOINCREMENT,
                    date                VARCHAR(15),
                    memo                VARCHAR(150),
                    amount              INTEGER,
                    account_key         INTEGER,
                    person              VARCHAR(15),
                    snippet_key         INTEGER,
                    FOREIGN KEY (account_key) REFERENCES accounts(account_key),
                    FOREIGN KEY (snippet_key) REFERENCES snippets(snippet_key)
                );
        """
        conn.commit_query(create_transactions_table)


##TODO the loop I need to do is add transactions, go through unknown, make snippets and link to snippets


def main_menu():
    choices = [
        'view saved raw_data',
        'add new raw_data',
        'modify existing rules'
    ]
    keys = [
        quit_program,
        view_saved_data_menu,
        add_new_raw_data,
        modify_existing_rules_menu
    ]
    func_menu = Menu(
        'Main Menu',
        choices=choices,
        zero_choice='Exit',
        keys=keys
    )
    func = func_menu.prompt()
    func()


def quit_program():
    print('quitting')


def view_saved_data_menu():
    print('placeholder for view saved raw_data menu')
    pass


def make_table(account_key, raw_data):
    account_data = get_account_data(account_key)
    date_column = account_data['date_column']
    memo_column = account_data['memo_column']
    amount_column = account_data['amount_column']
    # find the header row by looking for the headers
    for row_num, row in enumerate(raw_data):
        if (date_column, memo_column, amount_column) in row:
            header_row = row_num
            break
    headers = raw_data[header_row]
    data = raw_data[header_row+1:]
    return PyTable(headers, data)


def get_filename_snippets():
    query = """
        SELECT 
            snippet_key,
            snippet,
            source_account_key
        FROM 
            snippets
        WHERE
            type_key IS NULL AND
            vendor_key IS NULL
    """
    with DbSession('persistent_data.db') as conn:
        return conn.fetch_query(query)


def get_all_accounts():
    query = """
        SELECT account_id
        FROM accounts
    """
    with DbSession as conn:
        accounts = conn.fetch_query(query)
    return accounts.get_column_as_list('account_id')


def get_all_vendors():
    query = """
        SELECT vendor_id
        FROM vendors
    """
    with DbSession as conn:
        vendors = conn.fetch_query(query)
    return vendors.get_column_as_list('vendor_id')


def get_account_key_from_prompt():
    account_id_menu = Menu(
        'Existing accounts',
        get_all_accounts(),
        return_choice=True
    )
    account_id = account_id_menu.prompt()
    query = f"""
        SELECT account_key
        FROM accounts
        WHERE account_id = '{account_id}'
    """
    with DbSession('persistent_data.db') as conn:
        return conn.fetch_single_value(query)


def get_vendor_key_from_prompt():
    vendor_id_menu = Menu(
        'Existing vendors',
        get_all_vendors(),
        return_choice=True,
        zero_choice='CREATE NEW VENDOR'
    )
    vendor_id = vendor_id_menu.prompt()
    if vendor_id == 'CREATE NEW VENDOR':
        return vendor_id
    query = f"""
        SELECT vendor_key
        FROM vendors
        WHERE vendor_id = '{vendor_id}'
    """
    with DbSession('persistent_data.db') as conn:
        return conn.fetch_single_value(query)


def get_account_key(filename, sample_data):
    # get the snippets from database for matching accounts to filenames
    filename_snippets = get_filename_snippets()
    for row in filename_snippets:
        snippet = row['snippet']
        if snippet in filename:
            account_key = row['source_account_key']
            break
    else:  # it's a new file type?
        print('Existing accounts:')
        for account in get_all_accounts():
            print(f'\t{account}')
        print('\n\n')
        print(f'No account found for {filename}.\n'
              f'1) add account\n'
              f'2) add rule for exis iting account\n'
              f'0) skip this raw_data\n')
        response = input()
        if response not in ('1', '2', '0'):
            print('invalid entry')
            get_account_key(filename)
        if response == '1':
            account_key = create_new_account(filename, sample_data)
            add_snippet_to_db(filename, account_key)
        elif response == '2':
            account_key = get_account_key_from_prompt()
            add_snippet_to_db(filename, account_key)
        else:  # if they said skip, skip this loop
            return 'continue'
    return account_key


def add_new_raw_data():
    """workflow for adding new raw_data to the program storage"""
    # first we copy the raw_data over so we have it
    # user gives filepath to new raw_data (have it all in a folder)
    print('enter filepath for new raw_data and press enter, or just press enter to go back:\n\n')
    filepath = input()

    # session copies raw_data to 'raw raw_data' subfolder in session folder
    session_filepath = os.getcwd()  # save current directory for later
    os.chdir(filepath)  # change to the specified filepath
    csv_objects = get_csv_objects()  # copy all the csv files
    os.chdir(session_filepath)  # go back to the session
    os.chdir('raw_data')  # move into the raw raw_data folder
    # copy into filepath
    for filename, data in csv_objects.items():
        to_csv(data, filename)
    os.chdir('..')  # go back to the base filepath

    # take that raw_data already in memory and start processing it for adding to the processed data folder
    for filename, data in csv_objects.items():
        # the following should be refactored into a "get account" function
        account_key = get_account_key(filename, data)
        if account_key == 'continue':
            continue
        # now that we have the account key, get the account
        table = make_table(account_key, data)
        # just the row, if I need to access the PyTable functionality later I'll have to drop the [0]
        account_data = get_account_data(account_key)[0]

        table.select_columns(
            account_data['date_column'],
            account_data['memo_column'],
            account_data['amount_coulumn']
        )
        table.headers = ['Date', 'Memo', 'Amount']
        table.to_csv(filepath)


def create_new_account(filename, sample_data):
    # name the account
    account_name = input('new account name:   >')
    # highlight the part of the snippet that makes it so
    print(filename)
    print('please enter the part of the filename you would like\n'
          'matched to use this account type in the future')
    snippet = input()
    # show all existing files that will match
    add_snippet_to_db(snippet, account_name)
    # show sample data and prompt for date column, memo column and amount column
    HeadlessData(sample_data).print(num_rows=15)
    date_column = input('\nPlease enter the header for the date column')
    memo_column = input('\nPlease enter the header for the memo column')
    amount_column = input('\nPlease enter the header for the amount column')
    # show all vendors that say internal account and say to choose one or add one
    vendor_key = get_vendor_key_from_prompt()  # store the corresponding vendor key
    if vendor_key == 'CREATE_NEW_VENDOR':
        vendor_key = add_vendor_to_db()
    # add the row to the table and then query it for the key and return it
    return add_account_to_db(account_name, date_column, memo_column, amount_column, vendor_key)


def add_vendor_to_db(vendor_id, is_internal_account: bool = False, typical_type=None):
    insert_query = f"""
        INSERT INTO vendors
        (vendor_id, is_internal_account, typical_type)
        VALUES
            ({vendor_id}, {int(is_internal_account)}, {typical_type}
    """
    fetch_query = f"""
        SELECT vendor_key
        FROM vendors
        WHERE vendor_id = '{vendor_id}'
    """
    with DbSession as conn:
        conn.commit_query(insert_query)
        return conn.fetch_single_value(fetch_query)


def add_account_to_db(account_id, date_column, memo_column, amount_column, vendor_key):
    insert_query = f"""
        INSERT INTO accounts
        (account_id, date_column, memo_column, amount_column, vendor_key)
        VALUES
            ({account_id}, {date_column}, {memo_column}, {amount_column}, {vendor_key})
    """
    fetch_query = f"""
        SELECT account_key
        FROM accounts
        WHERE account_id = '{account_id}'
    """
    with DbSession as conn:
        conn.commit_query(insert_query)
        return conn.fetch_single_value(fetch_query)


def add_snippet_to_db(snippet, source_account_key, vendor_key=None, type_key=None):
    insert_query = f"""
        INSERT INTO snippets
        (snippet, source_account_key, vendor_key, type_key)
        VALUES
            ({snippet}, {source_account_key}, {vendor_key}, {type_key})
    """
    fetch_query = f"""
        SELECT snippet_key
        FROM snippets
        WHERE 
            snippet = '{snippet}' and
            source_account_key = '{source_account_key}'
    """
    with DbSession as conn:
        conn.commit_query(insert_query)
        return conn.fetch_single_value(fetch_query)


def get_csv_objects():
    """gets all csv objects from current directory. returns a dict with filename: object pairs"""
    dict_out: Dict[str: List[list]] = {}
    for file in os.listdir():
        if not file.endswith('.csv'):
            print(f'skipping {file}')
            continue
        print(f'loading {file}')
        dict_out[file] = from_csv(file)
    return dict_out


def modify_existing_rules_menu():
    print('placeholder for modify existing rules menu')
    pass


def main():
    # program runs
    # use prompts to get into a consistent folder
    get_session()
    # user chooses view or modify (only modify if new)
    main_menu()

    # session opens the first raw_data file
    # -if filenames gets a hit, process the file in the way of that account
    # prompt user to type in the column name of each of 'Date', 'Memo', 'Amount'
    # program trims and re-orders the file thusly, then adds the "account" and "bank" fields.
    # add to processed raw_data folder and save csv
    # add corresponding column headers to the accounts table
    # loop all raw_data files

    # go through all raw transactions
    # first make sure there are no exact matches in transactions table
    # next check all for hits from snippets.
    # print a pivot table for types

    # prompt user to go through a type or upload to db
    # -if type
    # -user enters row number to examine
    # -copy a snippet
    # -show all matches for that snippet, prompt to modify it, go back or add a vendor/type
    # -if vendors or types are added, add to snippets
    # -vendors/types should be checked against existing ones, added if new.
    # -repeat until user exits
    # if upload, raw_data is added to db to save it


if __name__ == '__main__':
    main()
