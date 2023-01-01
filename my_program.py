from typing import Callable, List, Any, Dict, Tuple
import os
import pandas
import sqlite3
from pandas_utilities import PyTable
from sqlite_utilities import DbSession


# boilerplate


class Menu:
    """A class for creating and interacting with a menu. When deployed, it prints out a 1-num indexed list of choices.
    when the user enters one of the numbers, they choose that choice. what is returned depends on the choice format.

    The choices can be a list with items in one of three formats:
    1. 'indexed': A list of strings representing the choices. In this case, the menu will return the position
        of the choice in the list, starting at 0.
    2. 'keyed': A list of tuples, where each tuple contains a string representing the choice and any object to be
        returned when the choice is selected.
    3. 'mirrored': A list of tuples, where each tuple contains a single string representing the choice. The value
        returned when the choice is selected will be the same as the choice.

    Args:
        title (str): The title of the menu.
        choices (List[str | tuple]): A list of choices for the menu.
        zero_choice (str | tuple, optional): A special choice to be displayed at the bottom of the menu. it should be
            formatted like the items in the 'choices' list
    """

    @classmethod
    def deploy(cls,
               title: str,
               choices: List[str | tuple],
               zero_choice: str | tuple = None):
        menu = Menu(title, choices, zero_choice)
        return menu.prompt()

    def __init__(self,
                 title: str,
                 choices: List[str | tuple],
                 zero_choice: str | tuple = None):
        # explicit attributes
        self.title = title
        self._menu_type = self.get_menu_type(choices)
        self.choices = choices
        self.zero_choice = zero_choice
        self._selection = None

    @staticmethod
    def get_menu_type(choices) -> str | None:
        """Determine the type of menu based on the format of the choices.
        Args:
            choices (List[str | tuple]): A list of choices for the menu.

        Returns:
            str | None: The type of the menu, or None if the choices are not in a recognized format.
        """

        def item_type(item_in):
            """returns the menu types for all valid choice inputs"""
            if isinstance(item_in, str):
                return 'indexed'
            if isinstance(item_in, tuple) and isinstance(item_in[0], str):
                if len(item_in) == 1:
                    return 'mirrored'
                elif len(item_in) == 2:
                    return 'keyed'
            raise Exception(f"invalid item type for item {item_in}")

        menu_type_list = [item_type(item) for item in choices]
        # if its homogeneous return its first item
        first_item = menu_type_list[0]
        if all(menu_type == first_item for menu_type in menu_type_list):
            return menu_type_list[0]
        else:
            raise Exception('choice input list not of consistent format')

    @property
    def num_choices(self):
        return len(self.choices)

    @property
    def menu_type(self) -> str:
        """The menu's type, always a string.

        Returns:
            'indexed', 'mirrored', 'keyed'
        """
        return self._menu_type

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, new_value):
        if new_value is None:
            self._selection = None
        if isinstance(new_value, str):
            try:
                selection = int(new_value)
            except ValueError:
                raise ValueError(f'input must be an integer, selecting a menu item. you entered {new_value}')
        else:
            raise TypeError('selection must be a string')
        if selection > self.num_choices:
            raise IndexError(f'there were a maximum of {self.num_choices} choices, you entered {selection}')
        if selection == 0:
            if self.zero_choice:
                self._selection = 0
            else:
                raise IndexError(f"this menu has no valid return for input '0'")
        self._selection = selection

    def print(self):
        # get everything in the right string format
        choice_string = [choice if self.menu_type == 'indexed' else choice[0] for choice in self.choices]
        # print it out
        print('\n')
        print(self.title)
        print()
        for ii, choice in enumerate(choice_string):
            print(f'{ii + 1}: {choice}')
        if self.zero_choice:
            zero_choice_string = self.zero_choice if self.menu_type == 'indexed' else self.zero_choice[0]
            print(f'0: {zero_choice_string}\n')

    def prompt(self) -> Any:
        # print self out
        self.print()
        # prompt for input, selection has validation built into it and will convert to int
        self.selection = input('> ')
        # we know the selection will be valid if it got this far
        if self.menu_type == 'indexed':
            return self.selection
        if self.menu_type == 'mirrored':
            return_list = [self.zero_choice[0]] + [choice[0] for choice in self.choices]
        elif self.menu_type == 'keyed':
            return_list = [self.zero_choice[1]] + [choice[1] for choice in self.choices]
        else:  # only its always possible I havent coded it yet
            raise Exception(f'no prompt made yet for menu type {self.menu_type}')
        if self.selection > len(return_list)-1:
            return self.prompt()
        else:
            return return_list[self.selection]


class Table(pandas.DataFrame):
    """a wrapper for a pandas dataframe. basically just adding some functionality if needed"""
    pass


def quit_program():
    print('quitting')


# start menu

def start_menu() -> None:
    """navigates us into an environment where we have a consistent directory tree to work with."""
    # navigate to the "sessions" directory
    os.chdir('sessions')
    # this is where all the sessions are saved
    saved_sessions = os.listdir()
    # don't bother with a menu if there are no saved sessions
    if len(saved_sessions) == 0:
        session = 'new session'
    # ask user to choose one, or make a new session
    else:
        session = Menu.deploy(
            title='Choose a session:',
            choices=[(filename,) for filename in saved_sessions],
            zero_choice=('new session',)
        )
    if session == 'new session':
        create_new_session()
    else:
        os.chdir(session)


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
        # add default 'types' to db
        add_default_types = """
            INSERT INTO types
            (type_id)
            VALUES
                ('Transfer')
        """
        conn.commit_query(add_default_types)
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


# main menu

def main_menu():
    session_name = os.path.basename(os.getcwd())
    func = Menu.deploy(
        title=f'{session_name}: Main Menu',
        choices=[
            ('view saved data', view_saved_data_menu),
            ('add new data', add_new_data)
        ],
        zero_choice=('Exit', quit_program)
    )
    func()


def view_saved_data_menu():
    func = Menu.deploy(
        title='Saved data menu',
        choices=[
            ('Browse DB', db_browser),
            ('read trimmed data', open_processed_csv)
        ],
        zero_choice=('Back', main_menu)
    )
    func()


def add_new_data():
    """workflow for adding new raw_data to the program storage"""

    # user gives filepath to new data, program reads data
    filepath = input('enter filepath for new raw_data and press enter, or just press enter to go back:\n'
                     '> ')
    if filepath == '':
        main_menu()
    if not filepath.endswith('.csv'):
        raise Exception('data must be from a csv file')
    filename = os.path.basename(filepath)
    data = pandas.read_csv(filepath)

    # program copies it into the raw_data folder
    os.chdir('raw_data')  # go into the folder
    data.to_csv(filename, index=False)  # 'paste it'
    os.chdir('..')  # go back to the base filepath

    # process the data
    account_key = get_account_key_from_filename(filename)  # attempt to autodetect the account
    if account_key is None:  # if not, get it from the user
        account_key = get_account_key_from_prompt(filename, data)
    account_data = get_account_data(account_key)  # get the information from the database for parsing the file
    table = make_table(account_data, data)  # format the table
    columns_to_keep = [
        account_data['date_column'],
        account_data['memo_column'],
        account_data['amount_column']
    ]  # get the column headers we want from account_data
    table = table.loc[:, columns_to_keep]  # filter columns
    clean_headers = [
        'Date',
        'Memo',
        'Amount'
    ]  # clean headers to replace old ones with
    table.rename(columns=dict(zip(columns_to_keep, clean_headers)))  # rename columns

    # put the processed data into processed data folder
    os.chdir('processed_data')  # go into the folder
    table.to_csv(filename, index=False)  # 'paste it'
    os.chdir('..')  # go back to base filepath

    # go back to main menu
    main_menu()


# user interactions

def db_browser():
    with sqlite3.connect('persistent_data.db') as conn:
        user_input = ''
        while user_input.upper() != 'EXIT':
            user_input = input('\n\nnew query:\n')
            if user_input.upper() not in ('', 'EXIT', 'COMMIT'):
                try:
                    results = pandas.read_sql_query(user_input, conn)
                    print(results.to_string())
                except TypeError as err:
                    print(f"WARNING: '{err}' thrown, ignore if you entered an update query")
                except pandas.errors.DatabaseError as err:
                    print(f"WARNING: '{err}' thrown")
            if user_input.upper() == 'COMMIT':
                conn.commit()
    view_saved_data_menu()


def open_processed_csv():
    os.chdir('processed_data')
    processed_files = os.listdir()
    file = Menu.deploy(
        title='Choose a file',
        choices=[(processed_file,) for processed_file in processed_files],
        zero_choice=('Back',)
    )
    if file == 'Back':
        os.chdir('..')
        view_saved_data_menu()
    else:
        data = pandas.read_csv(file)
        print(data.to_string())
        input('press enter to go back')
        os.chdir('..')
        view_saved_data_menu()


def create_new_account(filename, sample_data: pandas.DataFrame) -> str:
    # name the account
    account_name = input(f"new account name for '{filename}':\n"
                         '> ')
    # highlight the part of the snippet that makes it so
    print(filename)
    snippet = input('please enter the part of the filename you would like\n'
                    'matched to use this account type in the future\n'
                    '> ')
    # show sample data and prompt for date column, memo column and amount column
    print('sample data:')
    print(sample_data.to_string(max_rows=10))
    date_column = input('\nPlease enter the header for the date column\n'
                        '> ')
    memo_column = input('\nPlease enter the header for the memo column\n'
                        '> ')
    amount_column = input('\nPlease enter the header for the amount column\n'
                          '> ')
    # show all vendors that say internal account and say to choose one or add one
    vendor_key = get_vendor_key_from_prompt(account_name)  # store the corresponding vendor key
    # add the row to the table and then query it for the key and return it
    account_key = add_account_to_db(account_name, date_column, memo_column, amount_column, vendor_key)
    add_snippet_to_db(snippet, account_key)
    return account_name


def get_account_key_from_prompt(filename, data) -> int:
    # get a list of account id's if possible, prompt user for choice
    all_accounts = get_all_accounts()
    if len(all_accounts) != 0:
        account_id = Menu.deploy(
            title=f"No account detected for '{filename}'",
            choices=[(account,) for account in all_accounts],
            zero_choice=('create new account',)
        )
    else:
        account_id = 'create new account'
    # if no accounts in db or if user wishes, create a new account
    if account_id == 'create new account':
        account_id = create_new_account(filename, data)
    # get the account key from that account id and return it
    query = f"""
        SELECT account_key
        FROM accounts
        WHERE account_id = '{account_id}'
    """
    with DbSession('persistent_data.db') as conn:
        return int(conn.fetch_single_value(query))


def get_vendor_key_from_prompt(account_id) -> int:
    vendors = get_all_vendors()
    if len(vendors) != 0:
        vendor_id = Menu.deploy(
            title=f'Choose a vendor for {account_id}',
            choices=[(vendor,) for vendor in sorted(vendors)],
            zero_choice=('CREATE NEW VENDOR',)
        )
    else:
        vendor_id = 'CREATE NEW VENDOR'

    if vendor_id == 'CREATE NEW VENDOR':
        vendor_id = input('new vendor id:\n'
                          '> ')
        transfer_key = get_type_key_from_id('Transfer')
        add_vendor_to_db(vendor_id, is_internal_account=True, typical_type_key=transfer_key)
    query = f"""
        SELECT vendor_key
        FROM vendors
        WHERE vendor_id = '{vendor_id}'
    """
    with DbSession('persistent_data.db') as conn:
        return int(conn.fetch_single_value(query))


# DB interactions


def get_account_key_from_filename(filename):
    """Returns the source account key for a given filename, or None if no matching account is found.

    :param filename: The filename to search for.
    :return: The source account key for the matching account, or None if no match is found.
    """
    # get the snippets from database for matching accounts to filenames
    filename_snippets = get_filename_snippets()
    if filename_snippets.empty:  # return none if the snippets table is empty
        return None
    for ind, row in filename_snippets.iterrows():
        snippet = row['snippet']
        if snippet in filename:
            return row['source_account_key']
    else:
        return None


def get_account_key_from_id(account_id):
    query = f"""
        SELECT account_key
        FROM accounts
        WHERE account_id = `{account_id}`
    """
    with DbSession('persistent_data.db') as conn:
        account_key = conn.fetch_single_value(query)
    return account_key


def get_type_key_from_id(type_id) -> int:
    query = f"""
        SELECT type_key
        FROM types
        WHERE type_id = '{type_id}'
    """
    with DbSession('persistent_data.db') as conn:
        type_key = conn.fetch_single_value(query)
    return int(type_key)


def get_all_accounts() -> list:
    query = """
        SELECT account_id
        FROM accounts
    """
    with DbSession('persistent_data.db') as conn:
        accounts = conn.fetch_column(query)
    return accounts


def get_all_vendors() -> list:
    query = """
        SELECT vendor_id
        FROM vendors
    """
    with DbSession('persistent_data.db') as conn:
        vendors = conn.fetch_column(query)
    return vendors


def get_filename_snippets() -> pandas.DataFrame:
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


def get_account_data(account_key: str) -> pandas.Series:
    query = f"""
        SELECT * FROM accounts
        WHERE account_key = {account_key}
    """
    with DbSession('persistent_data.db') as conn:
        account_data = conn.fetch_query(query)
    return account_data.iloc[0]


def add_vendor_to_db(vendor_id, is_internal_account: bool = False, typical_type_key=None):
    insert_query = f"""
        INSERT INTO vendors
        (vendor_id, is_internal_account, typical_type_key)
        VALUES
            ('{vendor_id}', {int(is_internal_account)}, {typical_type_key})
    """
    fetch_query = f"""
        SELECT vendor_key
        FROM vendors
        WHERE vendor_id = '{vendor_id}'
    """
    with DbSession('persistent_data.db') as conn:
        conn.commit_query(insert_query)
        return conn.fetch_single_value(fetch_query)


def add_account_to_db(account_id, date_column, memo_column, amount_column, vendor_key):
    insert_query = f"""
        INSERT INTO accounts
        (account_id, date_column, memo_column, amount_column, vendor_key)
        VALUES
            ('{account_id}', '{date_column}', '{memo_column}', '{amount_column}', {vendor_key})
    """
    fetch_query = f"""
        SELECT account_key
        FROM accounts
        WHERE account_id = '{account_id}'
    """
    with DbSession('persistent_data.db') as conn:
        conn.commit_query(insert_query)
        return int(conn.fetch_single_value(fetch_query))


def add_snippet_to_db(snippet, source_account_key, vendor_key=None, type_key=None):
    vendor_key = 'NULL' if vendor_key is None else vendor_key
    type_key = 'NULL' if type_key is None else type_key
    insert_query = f"""
        INSERT INTO snippets
        (snippet, source_account_key, vendor_key, type_key)
        VALUES
            ('{snippet}', {source_account_key}, {vendor_key}, {type_key})
    """
    fetch_query = f"""
        SELECT snippet_key
        FROM snippets
        WHERE 
            snippet = '{snippet}' and
            source_account_key = '{source_account_key}'
    """
    with DbSession('persistent_data.db') as conn:
        conn.commit_query(insert_query)
        return conn.fetch_single_value(fetch_query)


# processing functions


def make_table(account_data: pandas.Series, raw_data: pandas.DataFrame) -> pandas.DataFrame:
    date_column = account_data['date_column']
    memo_column = account_data['memo_column']
    amount_column = account_data['amount_column']
    # first lets see if the dataframe handled it for us already
    target_headers = (date_column, memo_column, amount_column)
    if all(header in raw_data.columns for header in target_headers):
        return raw_data
    # find the header row by looking for the headers
    for row_num, row in enumerate(raw_data.values.tolist()):
        if (date_column, memo_column, amount_column) in row:
            header_row = row_num
            break
    else:  # if we got this far then we failed to parse it
        # If the header row is not found, raise an exception
        raise ValueError('Header row not found in DataFrame')
    headers = raw_data.iloc[header_row]
    data = raw_data.iloc[header_row + 1:]
    return pandas.DataFrame(data, columns=headers)


# execution


def main():
    # program runs
    # use prompts to get into a consistent folder
    start_menu()
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
