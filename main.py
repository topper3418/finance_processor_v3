from PySheets import PySheet, PyTable
import os
from typing import List
from datetime import datetime


def get_csv_filepaths_from_directory(directory_path):
    # Create an empty list to store the filepaths
    csv_filepaths = []

    # Use the os.listdir() method to get a list of all files and directories in the
    # specified directory.
    for item in os.listdir(directory_path):
        # Use the os.path.join() method to construct the full filepath of the item
        filepath = os.path.join(directory_path, item)

        # Check if the filepath is a CSV file by checking the file extension
        if filepath.endswith('.csv'):
            # If the filepath is a CSV file, add it to the list of filepaths
            # Use double backslashes in the filepath to ensure it is properly formatted
            # for use in Windows
            if os.name == 'nt':
                full_filepath = filepath.replace('/', '\\')
            else:
                full_filepath = filepath
            csv_filepaths.append(full_filepath)

    # Return the list of filepaths
    return csv_filepaths


def check_lookup(lookup_value, lookup_dict):
    """takes in a thing to check and a lookup. if any of the matching values are in the lookup, it returns the key"""
    for key, snippet_list in lookup_dict.items():
        if any(snippet in lookup_value for snippet in snippet_list):
            out_value = key
            break
    else:
        out_value = 'UNKNOWN'
    return out_value


def get_filename_from_filepath(filepath):
    # Use the os.path.split() method to split the filepath into a tuple containing the
    # directory path and the filename.
    # This method will handle any necessary platform-specific adjustments to the filepath
    # so that it can be properly split.
    directory_path, filename = os.path.split(filepath)

    # Return the filename
    return filename.split('.')[0]


def get_chase_table(filepath):
    sheet = PySheet(filepath)
    table = sheet.py_table()
    table.drop_columns(['Post Date', 'Category', 'Type', 'Memo'])
    table.headers = ['Date', 'Memo', 'Amount']
    # get vendor
    vendor_lookup = {
        'Target': ['target'],
        'Panda Express': ['Panda',
                          'PANDA EXPRESS'],
        'Tesla': ['tesla'],
        'Walgreens': ['WALGREENS #'],
        'Etsy': ['Etsy.com'],
        'Wetzels Pretzels': ['WETZELS PRETZELS'],
        'UPS': ['THE UPS STORE'],
        'Comcast': ['comcast california'],
        'Waste Management': ['waste mgmt'],
        'Designer Shoe Warehouse': ['dsw dublin retail'],
        'Parking Sacramento': ['ABMONSITEGOLDEN1CENTER'],
        'Transfer from WF': ['payment thank you-mobile',
                             'payment thank you - web',
                             'automatic payment - thank'],
        'Chick-fil-a': ['chick-fil-a'],
        'Tesla food': ['365 market'],
        'BevMo': ['BEVERAGES &amp; MORE'],
        'Mission Peak sports store': ['TST* Mission Peak '],
        'Old Greenwood BBQ': ['OLD GREENWOOD BBQ'],
        'Pho Tai': ['pho tai'],
        'Mexical': ['MEXICAL'],
        'Hulu': ['hlu*hulu'],
        'Roadside Rotisserie': ['ROADSIDE ROTISSERIE'],
        'Spencers': ['spencer gifts'],
        'JBA investment group': ['JBA INVESTMENT GROUP LLC'],
        'Tesla Insurance': ['tesla insurance services'],
        '76 store': ['76 - Shop N go'],
        'In N Out': ['in n out burger'],
        '7-11': ['7-eleven'],
        'Party time liquor': ['party time liquor'],
        'CVS': ['cvs/pharmacy'],
        'Carls Jr': ['carls jr'],
        'Yoshi food truck': ['sq *yoshi'],
        'Grillzillas': ['sq *grillzillas'],
        'Cravings': ['sq *cravings'],
        'Dollar Shave Club': ['dollarshaveclubus'],
        'The faculty club (uc berkeley)': ['the faculty club'],
        'Funimation': ['paypal *Funimation'],
        'Mens Wearhouse': ['mens wearhouse'],
        'Speedy Panini food truck': ['sq *speedy panini'],
        'Azazie': ['Azazie inc'],
        'Safeway': ['safeway #'],
        'Jamba juice': ['tst* jamba juice',
                        'jamba juice',
                        'jambajuic'],
        "O'Reilly": ["o'reilly auto parts"],
        "Robert's Parking": ["robert's parking"],
        'Air BnB': ['airbnb'],
        'Star Pizza': ['the star on park'],
        'Office max': ['officemax/depot'],
        'Playstation': ['playstation network'],
        "Dominoes": ["domino's"],
        'Fogo de Chao': ['fogo de chao',
                         'tsp*fogodechao'],
        'Unknown parking meter': ['parkingmeter4'],
        'Poke Don': ['poke don hayward'],
        "Lou Malnati's": ['lou malnatis - michigan'],
        'Residence Inn': ['residence inn'],
        'Hertz': ['hertz'],
        'Blue Bottle Coffee': ['sq *blue bottle coffee'],
        "Maggie's be Cafe": ["sq *maggie's be cafe"],
        "Texas Roadhouse": ['texas roadhouse #'],
        'Bark Box': ['bark&amp;co (barkbox'],
        'Home Depot': ['the home depot'],
        'Kaiser': ['kaiser pharm'],
        'Costco': ['costco whse'],
        'Poke House': ['poke house 2'],
        'Valero': ['winton valero'],
        'Tellus Coffee': ['tellus coffee'],
        'Alameda Elks Lodge': ['sq *alameda elks 1015'],
        'Ramen 101': ['ramen 101.'],
        'Hayward Water': ['Hayward self service'],
        'Seafood City Supermarket': ['seafood city superm'],
        'Lowes': ['Lowes #'],
        'Chase (interest)': ['purchase interest charge'],
        'Chase (fee)': ['annual membership fee'],
        'Mark Ericson (oral surgeon)': ['mark s ericson dds'],
        "Capelo's Barbecue": ['sq * capelo',
                              'sq *capelo'],
        'Bamboo Steamer': ['yelp-grubhubbamboos'],
        'Fastrak': ['fastrak csc'],
        'Wellbrook Chiropractor': ['wellbrook family chiro'],
        'SkillShare': ['skillshare'],
        'Sport Clips': ['sport clips - ca'],
        "Nature's Good Guys": ['sp * naturesgoodguys'],
        'Canteen Vending': ['usa*canteen vending'],
        "Jimmy's": ['precision auto care'],
        "Cardena's Market": ['cardenas markets'],
        "Oakland A's": ['amk oakland'],
        'Twister': ['sq *twister'],
        'Sunrise Deli': ['sq* sunrise deli',
                         'sq *sunrise deli'],
        'Stadium Pub': ['the stadium pub'],
        'Saigon Street Food': ['sq *saigon street food'],
        'New Earth Market': ['new earth market'],
        'La Fondita': ['sq *la fondita kitchen'],
        'Rich & Sals Sport Shop': ['RICH &amp; SALS SPORT SHOP'],
        'Coldstone': ['coldstone creamy'],
        'Iron Door Saloon': ['iron door saloon'],
        'Pilot': ['pilot_',
                  'pilot    '],
        'Enterprise': ['enterprise rent-a-car'],
        'tickets.com': ['tickets.com i'],
        'Smart & Final': ['smart and final'],
        'Chevron': ['chevron '],
        'Banana Leaf inc': ['banana leaf inc'],
        'Apple': ['apple store  '],
        'Joe the Juice': ['joe  the juice new york'],
        'Limitless Axes': ['tst* limitless axes',
                           'LIMITLESSAXES.COM'],
        'REI': ['rei #'],
        'Eureka': ['sq *eureka'],
        'Share Tea': ['sq *sharetea'],
        'Emotion Beauty Salon': ['emotion beauty salon'],
        'GoGo Sushi': ['gogo sushi &amp; b.b.q'],
        'Kokoro Ramen': ['kokoro ramen'],
        'Dustyn Graham': ['gofndme* dustyn graham'],
        'Smile Direct Club': ['smiledirectclub'],
        'CA DMV': ['ca dmv fee',
                   'state of calif dmv int'],
        'Spotify': ['spotify usa'],
        'Gentle Care': ['gentle care veterinary'],
        'TurboTax': ['intuit *turbotax'],
        'Almanac Beer': ['sq *almanac beer'],
        'Encinel Nursery': ['encinal nursery']
    }
    type_lookup = {
        'Groceries': ['Target',
                      'Safeway',
                      'Costco',
                      'Seafood City Supermarket',
                      'Smart & Final'],
        'Automotive': ['Tesla',
                       "O'Reilly",
                       "Jimmy's",
                       'CA DMV'],
        'Fast Food': ['Panda Express',
                      'Wetzels Pretzels',
                      'Chick-fil-a',
                      'Old Greenwood BBQ',
                      'Pho Tai',
                      'Mexical',
                      'Roadside Rotisserie',
                      'In N Out',
                      'Carls Jr',
                      'Yoshi food truck',
                      'Grillzillas',
                      'Cravings',
                      'Speedy Panini food truck',
                      'Jamba Juice',
                      'Dominoes',
                      'Poke Don',
                      'Poke House',
                      "Capelo's Barbecue",
                      'Bamboo Steamer',
                      'Canteen Vending',
                      "Cardena's Market",
                      'Twister',
                      'Sunrise Deli',
                      'Saigon Street Food',
                      'New Earth Market',
                      'La Fondita'],
        'Health/hygene': ['Walgreens',
                          'CVS',
                          'Dollar Shave Club',
                          'Kaiser',
                          'Mark Ericson (oral surgeon)',
                          'Wellbrook Chiropractor',
                          'Sport Clips',
                          'Emotion Beauty Salon',
                          'Smile Direct Club'],
        'Shopping': ['Etsy',
                     'Designer Shoe Warehouse',
                     'Spencers',
                     'Mens Wearhouse',
                     'Azazie',
                     'Office max',
                     'Apple'],
        'Shipping/Transportation': ['UPS',
                                    'Parking Sacramento',
                                    "Robert's Parking",
                                    'Unknown parking meter',
                                    'Fastrak',
                                    'Enterprise'],
        'Utilities': ['Comcast',
                      'Waste Management',
                      'Hayward Water'],
        'Transfer': ['Transfer from WF'],
        'Alcohol': ['BevMo',
                    'Party time liquor'],
        'Fitness': ['Mission Peak sports store',
                    'Rich & Sals Sport Shop',
                    'REI',
                    'EUREKA'],
        'Entertainment': ['Hulu',
                          'Funimation',
                          'Playstation',
                          'Skillshare',
                          'Spotify'],
        'Misc': ['JBA investment group',
                 'Pilot',
                 'Dustyn Graham'],
        'Junk Food': ['76 store',
                      '7-11',
                      'Valero',
                      'Coldstone',
                      'Chevron',
                      'Share Tea'],
        'Going Out': ['The faculty club (uc berkeley)',
                      'Air BnB',
                      'Star Pizza',
                      'Fogo de Chao',
                      "Lou Malnati's",
                      'Residence Inn',
                      'Blue Bottle Coffee',
                      'Hertz',
                      "Maggie's be cafe",
                      'Texas Roadhouse',
                      'Ramen 101',
                      'Tellus Coffee',
                      'Alameda Elks Lodge',
                      "Oakland A's",
                      'Stadium Pub',
                      'Iron Door Saloon',
                      'tickets.com',
                      'Banana Leaf inc',
                      'Limitless Axes',
                      'Joe the Juice',
                      'GoGo Sushi',
                      'Kokoro Ramen',
                      'Almanac Beer'],
        'Maisie': ['Bark Box',
                   'Gentle Care'],
        'Home Expense': ['Home Depot',
                         'Lowes',
                         "Nature's Good Guys",
                         'Encinel Nursery'],
        'Interest/Fees': ['Chase (interest)',
                          'Chase (fee)'],
        'Tax': ['TurboTax']
    }
    vendors = table.generate_list_from_lookup('Memo', vendor_lookup)
    table.add_column('Vendor', vendors)
    types = table.generate_list_from_lookup('Vendor', type_lookup)
    table.add_column('Type', types)
    table.add_column('Account', ['Chase'] * table.rows)
    return table


def get_wells_table(filepath):
    sheet = PySheet(filepath)
    table = sheet.py_table(['Date', 'Amount', 'Stars', 'Blanks', 'Memo'])
    table.select_columns(['Date', 'Memo', 'Amount'])
    vendor_lookup = {
        'Tesla Payroll': ['tesla motors, in payroll'],
        'PG&E': ['pgande web online'],
        'Chase': ['chase credit crd epay',
                  'chase credit crd autopay'],
        'Amazon': ['amz_storecrd_pmt',
                   'payment for amz storecard'],
        'Venmo': ['venmo payment',
                  'venmo cashout'],
        'Apple Cash': ['apple cash transfer',
                       'apple cash 1infiniteloop'],
        'Barclays': ['barclaycard'],
        'Wells Fargo': ['online transfer ref',
                        'online transfer from',
                        'online transfer to',
                        'interest payment',
                        'savings od protection',
                        'overdraft protection xfer'],
        'Etrade': ['e*trade ach'],
        'Best Buy': ['best buy auto pymt'],
        'Pramod Pai': ['bill pay pramod pai'],
        'Emily': ['cagigas emily'],
        'Verizon': ['verizon wireless payments'],
        'Garden of Eden': ['garden of eden hayward']
    }
    type_lookup = {
        'Income': ['Tesla Payroll'],
        'Utilities': ['PG&E',
                      'Verizon'],
        'Credit Card Payment': ['Chase',
                                'Amazon',
                                'Barclays'],
        'Transfer': ['Venmo',
                     'Apple Cash',
                     'Wells Fargo',
                     'Etrade',
                     'Best Buy'],
        'Weed': ['Garden of Eden'],
        'Rent': ['Pramod Pai',
                 'Emily']
    }
    vendors = table.generate_list_from_lookup('Memo', vendor_lookup)
    table.add_column('Vendor', vendors)
    types = table.generate_list_from_lookup('Vendor', type_lookup, exact_match=True)
    table.add_column('Type', types)
    table.add_column('Account', [get_filename_from_filepath(filepath)] * table.rows)
    return table


def get_apple_table(filepath):
    sheet = PySheet(filepath)
    table = sheet.py_table()
    table.select_columns(['Transaction Date', 'Description', 'Amount (USD)'])
    table.headers = ['Date', 'Memo', 'Amount']
    vendor_lookup = {
        'Monarch Bay Golf club': ['monarch bay golf club'],
        'Target': ['Target'],
        'Safeway': ['Safeway'],
        'Clubhouse': ['tst* mission peak spor'],
        'Wells Fargo': ['ach deposit internet transfer'],
        'Yo-Kai Express': ['yo-kai express'],
        'Work kiosk': ['365 market 888'],
        'Comcast': ['comcast california'],
        'Two Pitchers brewing': ['pp*two pitchers brewi'],
        'Oakland': ['oakland park meter ips'],
        'Steam': ['steam purchase']
    }
    type_lookup = {
        'Health/Fitness': ['Monarch Bay Golf club'],
        'Shopping': ['Target',
                     'Safeway'],
        'Fast Food': ['Yo-Kai Express'],
        'Going Out': ['Clubhouse',
                      'Two Pitchers brewing'],
        'Cash Transfer': ['Wells Fargo'],
        'Junk Food': ['Work kiosk'],
        'Utilities': ['Comcast'],
        'Taxes/fees': ['Oakland'],
        'Entertainment': ['Steam']
    }
    vendors = table.generate_list_from_lookup('Memo', vendor_lookup)
    table.add_column('Vendor', vendors)
    types = table.generate_list_from_lookup('Vendor', type_lookup, exact_match=True)
    table.add_column('Type', types)
    table.add_column('Account', ['Apple'] * table.rows)
    return table


def get_all_tables(filepath_list: List[str]) -> List[PyTable]:
    filename_lookup = {
        get_chase_table: ['Chase'],
        get_wells_table: ['Checking',
                          'PreferredChecking',
                          'Savings'],
        get_apple_table: ['Apple']
    }
    tables = []
    for filepath in filepath_list:
        parsing_func = check_lookup(filepath, filename_lookup)
        if parsing_func == 'UNKNOWN':
            print(f'No appropriate parsing method found for {filepath}')
            continue
        tables.append(parsing_func(filepath))
    return tables


if __name__ == '__main__':
    # load everything into the correct object type
    filepaths = get_csv_filepaths_from_directory(
        '/Users/travisopperud/Documents/GitHub/finance_processor_v3/Data'
    )
    tables = get_all_tables(filepaths)
    all_table = tables[0]
    for table in tables[1:]:
        all_table += table


    # this chunk of code parses the date and orders it, filters it and un-parses it
    def parse_date(date_in):
        return datetime.strptime(date_in, '%m/%d/%Y')


    all_table.format_col('Date', parse_date)
    date_ind = all_table.get_index('Date')
    all_table.sort('Date', lambda row: row[date_ind], reverse=True)


    # this filters for august through november
    def filter_for_month(row_in):
        date: datetime = row_in[date_ind]
        year = date.year
        month = date.month
        in_november = year == 2022 and month == 11
        in_october = year == 2022 and month == 10
        in_september = year == 2022 and month == 9
        return in_november or in_october or in_september


    all_table.filter_by_func(filter_for_month)


    # this turns it back into a formatted string
    def format_date(date_in):
        return datetime.strftime(date_in, '%a %b %d, %Y')


    all_table.format_col('Date', format_date)

    pivot_table = all_table.pivot('Type', 'Amount')
    # print the results
    pivot_table.print()
