import csv
from models import db, ACH
import datetime

def is_credit(dict):
    dict['Transaction'] == "ACH Credits"
    return True

def is_vendor(dict):
    if 'Desc: COMM OF PA' in dict['Description']:
        return True

def add_to_db(row):
    credit = ACH(amount=row["Amount"], fund=row["AccountName"][-5:], description=row["Description"], received=row["AsOfDate"])
    db.session.add(credit)
    db.session.commit()

def process_ach(ach_file):
    with open(f'instance/ACH/{ach_file}', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if is_credit(row):
                if is_vendor(row):
                    add_to_db(row)
                   

