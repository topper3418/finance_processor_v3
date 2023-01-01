from typing import Callable, List, Any, Dict, Tuple
import os
import pandas
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
               zero_choice: str | Tuple[str, Any] = None):
        menu = Menu(title, choices, zero_choice)
        return menu.prompt()

    def __init__(self,
                 title: str,
                 choices: List[str | tuple],
                 zero_choice: str | Tuple[str, Any] = None):
        # explicit attributes
        self.title = title
        self._menu_type = self.get_menu_type(choices)
        if self.menu_type is None:
            raise Exception('warning, invalid menu type. see docstring for explanation on menu formats')
        if self.menu_type == 'inconsistent':
            raise Exception('warning, not all items in menu are of consistent format')
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
            return None

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
        print(self.title)
        for ii, choice in enumerate(choice_string):
            print(f'{ii + 1}: {choice}')
        if self.zero_choice:
            zero_choice_string = self.zero_choice if self.menu_type == 'indexed' else self.zero_choice[0]
            print(f'0: {zero_choice_string}\n')

    def prompt(self) -> Any:
        # print self out
        self.print()
        # prompt for input, selection has validation built into it and will convert to int
        self.selection = input('>')
        # we know the selection will be valid if it got this far
        if self.menu_type == 'indexed':
            return self.selection
        if self.menu_type == 'mirrored':
            return_list = [self.zero_choice[0]] + [choice[0] for choice in self.choices]
        elif self.menu_type == 'keyed':
            return_list = [self.zero_choice[1]] + [choice[1] for choice in self.choices]
        else:  # only its always possible I havent coded it yet
            raise Exception(f'no prompt made yet for menu type {self.menu_type}')
        return return_list[self.selection]


class Table(pandas.DataFrame):
    """a wrapper for a pandas dataframe. basically just adding some functionality if needed"""
    pass


def quit_program():
    print('quitting')


# start menu

def start_menu() -> None:
    """navigates us into an environment where we have a consistent directory tree to work with"""
    # navigate to the "sessions" directory
    os.chdir('sessions')
    # this is where all the sessions are saved
    saved_sessions = os.listdir()
    session = Menu.deploy(
        title='Choose a session:',
        choices=[tuple(filename) for filename in os.listdir()],
        zero_choice='new session'
    )
    print(f'you chose {session}')
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
    func = Menu.deploy(
        title='Main Menu',
        choices=[
            ('view saved data', view_saved_data_menu),
            ('add new data', add_new_data)
        ],
        zero_choice=('Exit', quit_program)
    )
    func()


def view_saved_data_menu():
    print('placeholder for view saved raw_data menu')
    main_menu()


def add_new_data():
    """workflow for adding new raw_data to the program storage
    Notes on the function tree:
    add_new_data todo make it all better annotated
        get_csv_objects
        get_account_key todo remake the menus in this, split into the sql and user input parts
            get_filename_snippets
            get_all_accounts
        make_table
            get_account_data
        get_account_data
            todo
        todo some kind of select_columns replacement

    """
    # first we copy the raw_data over so we have it
    # user gives filepath to new raw_data (have it all in a folder)
    print('enter filepath for new raw_data and press enter, or just press enter to go back:\n\n')
    filepath = input()
    if input == '':
        main_menu()

    # copy csv files to memory, paste them into new folder. not broken into a function
    session_filepath = os.getcwd()  # save current directory for later
    os.chdir(filepath)  # change to the specified filepath
    csv_objects = get_csv_objects()  # copy all the csv files
    os.chdir(session_filepath)  # go back to the session
    os.chdir('raw_data')  # move into the raw raw_data folder
    # copy into filepath
    for filename, data in csv_objects.items():
        data.to_csv(filename)
    os.chdir('..')  # go back to the base filepath

    # take that raw_data already in memory and start processing it for adding to the processed data folder
    for filename, data in csv_objects.items():
        # the following should be refactored into a "get account" function
        account_key = get_account_key(filename)
        if account_key is None:
            func = Menu(
                title='Account not detected in db from filename',
                choices=[
                    ('add new account', create_new_account),
                    ('add rule for existing account', add_snippet_to_db)
                ],
                zero_choice=('skip this file', lambda _: None)
            )
            account_key = func()
        if account_key == 'continue':
            continue
        # now that we have the account key, get the account
        table = make_table(account_key, data)
        # just the row, if I need to access the PyTable functionality later I'll have to drop the [0]
        account_data = get_account_data(account_key)[0]

        table.select_columns(
            account_data['date_column'],
            account_data['memo_column'],
            account_data['amount_column']
        )
        table.headers = ['Date', 'Memo', 'Amount']
        table.to_csv(filepath)


# add_new_data utilities

def get_account_key(filename):
    # get the snippets from database for matching accounts to filenames
    filename_snippets = get_filename_snippets()
    for row in filename_snippets:
        snippet = row['snippet']
        if snippet in filename:
            return row['source_account_key']
    else:
        return None


def create_new_account(filename, sample_data: pandas.DataFrame) -> int:
    # name the account
    account_name = input('new account name:   \n'
                         '>')
    # highlight the part of the snippet that makes it so
    print(filename)
    print('please enter the part of the filename you would like\n'
          'matched to use this account type in the future\n'
          '>')
    snippet = input()
    # show all existing files that will match
    add_snippet_to_db(snippet, account_name)
    # show sample data and prompt for date column, memo column and amount column
    print('sample data:')
    print(sample_data.to_string(max_rows=15))
    date_column = input('\nPlease enter the header for the date column\n'
                        '>')
    memo_column = input('\nPlease enter the header for the memo column\n'
                        '>')
    amount_column = input('\nPlease enter the header for the amount column\n'
                          '>')
    # show all vendors that say internal account and say to choose one or add one
    vendor_key = get_vendor_key_from_prompt()  # store the corresponding vendor key
    # add the row to the table and then query it for the key and return it
    return add_account_to_db(account_name, date_column, memo_column, amount_column, vendor_key)


# user interactions


def get_account_key_from_prompt() -> int:
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


def get_vendor_key_from_prompt() -> int:
    vendor_id = Menu.deploy(
        title='Existing vendors',
        choices=[tuple(vendor) for vendor in sorted(get_all_vendors())],
        zero_choice=tuple('CREATE NEW VENDOR')
    )
    if vendor_id == 'CREATE NEW VENDOR':
        vendor_id = input('new vendor id:\n'
                          '>')
        add_vendor_to_db(vendor_id, is_internal_account=True, typical_type='Transfer')
    query = f"""
        SELECT vendor_key
        FROM vendors
        WHERE vendor_id = '{vendor_id}'
    """
    with DbSession('persistent_data.db') as conn:
        return conn.fetch_single_value(query)


# DB interactions


def get_all_accounts() -> list:
    query = """
        SELECT account_id
        FROM accounts
    """
    with DbSession as conn:
        accounts = conn.fetch_query(query)
    return accounts.get_column_as_list('account_id')


def get_all_vendors() -> list:
    query = """
        SELECT vendor_id
        FROM vendors
    """
    with DbSession as conn:
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
        WHERE account_key = `{account_key}`
    """
    with DbSession('database.db') as conn:
        account_data = conn.fetch_query(query)
    return account_data.iloc[0]


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

# end add_new_data utilities



def make_table(account_key, raw_data):
    account_data = get_account_data(account_key)
    date_column = account_data['date_column']
    memo_column = account_data['memo_column']
    amount_column = account_data['amount_column']
    # find the header row by looking for the headers
    for row_num, row in enumerate(raw_data.values.tolist()):
        if (date_column, memo_column, amount_column) in row:
            header_row = row_num
            break
    else:
        # If the header row is not found, raise an exception
        raise ValueError('Header row not found in DataFrame')
    headers = raw_data.iloc[header_row]
    data = raw_data[header_row + 1:]
    return pandas.DataFrame(data, columns=headers)








def get_csv_objects() -> Dict[str: pandas.DataFrame]:
    """gets all csv objects from current directory. returns a dict with filename: object pairs"""
    dict_out: Dict[str: List[list]] = {}
    for file in os.listdir():
        if not file.endswith('.csv'):
            print(f'skipping {file}')
            continue
        print(f'loading {file}')
        dict_out[file] = pandas.read_csv(file)
    return dict_out


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
