import csv

def is_credit(dict):
    dict['Transaction'] == "ACH Credits"
    return True

def is_vendor(dict):
    if 'Desc: COMM OF PA' in dict['Description']:
        return True

def process_ach(ach_file):
    # print(f'*******************************This is your other print line {ach_file}')
    with open(f'instance/ACH/{ach_file}', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if is_credit(row):
                if is_vendor(row):
                    print(row)
                    print('****************************************************')
