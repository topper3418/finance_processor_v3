import pandas
import os


filepath = input('target csv file filepath:\n'
                 '> ')
filepath_head, filename = os.path.split(filepath)
os.chdir(filepath_head)
data = pandas.read_csv(filename)
with open('PRETTY '+filename, 'w') as file:
    file.writelines(data.to_string())
