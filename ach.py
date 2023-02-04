import csv

def is_credit(dict):
    dict['Transaction'] == "ACH Credits"
    return True

def is_vendor(dict):
    if 'Desc: COMM OF PA' in dict['Description']:
        return True

def process_ach(ach_file):
    with open(ach_file) as ach:
        reader = csv.DictReader(ach)
        for row in reader:
            if is_credit(row):
                if is_vendor(row):
                    print(row)
                    print('****************************************************')
