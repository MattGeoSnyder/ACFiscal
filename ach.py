import csv
from models import db, ACH, Department
import datetime
import re
import pdb

def is_credit(dict):
    return dict['Transaction'] == "ACH Credits"

def is_kane(row, description):
    key_words = ['KANE', '36 TREAS 310', 'HCCLAIMPMT','PROMISE MA']
    
    dep = Department.query.filter(Department.name == "Kane").first()
    
    bank = row["AccountName"][-5:]
    # pdb.set_trace()
    if bank == '11108':
        return dep.id
    elif bank == '11151':
        for word in key_words:
            if re.match(f'[\w\d\n\s\:-]*{word}[\w\d\n\s\:-]*', description):
                return dep.id

    return None

def is_health(row, description):
    dep = Department.query.filter(Department.name == "Health").first()

    if re.match("[\w\d\n\s\:-]*TSYS\/TRANSFIRST[\w\d\s\n\:-]*HEAL[\w\d\n\s\:-]*", description):
        return dep.id
    if re.match("[\w\d\n\s\:-]*DISBURSE[\w\d\n\s\:-]*INTELLIPAY[\w\d\n\s\:-]*", description):
        return dep.id
    if re.match('[\w\d\n\s\:-]*SMS GROUP INC[\w\d\n\s\:-]*', description):
        return dep.id
    return None

def is_emserv(row, description):
    dep = Department.query.filter(Department.name == "Emergency Services").first()

    if re.match("[\w\d\n\s\:-]*TSYS\/TRANSFIRST[\w\d\s\n\:-]*EMERGENCY SRVCS[\w\d\n\s\:-]*", description):
        return dep.id
    return None

def is_medex(row, description):
    dep = Department.query.filter(Department.name == "Medical Examiner's").first()

    if re.match("[\w\d\n\s\:-]*TSYS\/TRANSFIRST[\w\d\s\n\:-]*MEDICAL EXAMINER[\w\d\n\s\:-]*", description):
        return dep.id
    return None

def is_police(row, description):
    dep = Department.query.filter(Department.name == 'Police').first()

    if re.match("[\w\d\n\s\:-]*MISC PAY 015 TREAS 310[\w\d\s\n\:-]*POLI[\w\d\n\s\:-]*", description):
        return dep.id
    return None

def is_sheriff(row, description):
    dep = Department.query.filter(Department.name == 'Sheriff''s').first()

    if re.match("[\w\d\n\s\:-]*MISC PAY 015 TREAS 310[\w\d\s\n\:-]*SHER[\w\d\n\s\:-]*", description):
        return dep.id
    return None

def is_jail(row, description):
    dep = Department.query.filter(Department.name == 'Jail')

    if re.match('MISC PAY SSA', description):
        return dep.id
    if re.match('[\w\d\n\s\:-]*MISC PAY TREAS 310[\w\d\n\s\:-]*JAIL[\w\d\n\s\:-]*', description):
        return dep.id
    return None

def is_econ(row, description):
    dep = Department.query.filter(Department.name == 'Economic Development').first()

    if row['AccountName'][-5:] == '11106':
        return dep.id
    return None

def is_tax(row, description):
    dep = Department.query.filter(Department.name == 'Tax').first()

    if re.match('[\w\d\n\s\:-]*ALLEGHENY COUNTY TAX[\w\d\n\s\:-]*', description):
        return dep.id
    if re.match('[\w\d\n\s\:-]*ELECTRONIC LBX[\w\d\n\s\:-]*', description):
        return dep.id
    if re.match('[\w\d\n\s\:-]*ALLEGHENY CO HOTEL[\w\d\n\s\:-]*', description):
        return dep.id
    return None
    
def is_drink(row, description):
    dep = Department.query.filter(Department.name == 'Special Tax').first()

    if re.match('[\w\d\n\s\:-]*ALLEGHENY COUNTY DRIN[\w\d\n\s\:-]*', description):
        return dep.id
    if re.match('[\w\d\n\s\:-]*ALLEGHENY VEHICLE REN[\w\d\n\s\:-]*', description):
        return dep.id
    return None

def is_child(row, description):
    dep = Department.query.filter(Department.name == 'Fiscal').first()

    if re.match("[\d\w\n\s\:-]+PA-SCDU[\d\w\n\s\:-]*ALLEGHENY (COUNTY|CO) C[\d\w\n\s\:-]*", description):
        return dep.id
    return None

def is_parental(row, description):
    dep = Department.query.filter(Department.name == 'Fiscal').first()

    if re.match("[\d\w\n\s\:-]*PA-SCDU[\d\w\n\s\:-]*ALLEGHENY CO PARENTAL[\d\w\n\s\:-]*", description):
        return dep.id
    return None

def is_blood(row, description):
    dep = Department.query.filter(Department.name == 'Fiscal').first()

    if re.match("[\d\w\n\s\:-]*PA-SCDU[\d\w\n\s\:-]*ALLEGHENY COUNTY TREA[\d\w\n\s\:-]*", description):
        return dep.id
    return None

def is_parks(row, description):
    dep = Department.query.filter(Department.name == 'Parks').first()

    if re.match("[\w\d\n\s\:-]*GRANT CRDT[\w\d\s\n\:-]*RAD[\w\d\n\s\:-]*", description):
        return dep.id
    return None

def is_cage(credit, description):
    dep = Department.query.filter(Department.name == 'Cage').first()

    if re.match("[\w\d\n\s\:-]*MTOT[\w\d\n\s\:-]*", description):
        return dep.id
    return None

def categorize(credit):
    tests = [is_kane, is_health, is_emserv, is_medex, is_sheriff, is_police, is_jail, is_econ, is_tax, is_drink, is_child, is_parental, is_blood, is_parks, is_cage]

    for test in tests:
        dep_id = test(credit, credit['Description'])
        if dep_id:
            add_to_db(credit, dep_id)
            return
    add_to_db(credit, dep_id)
        
def add_to_db(row, dep_id):
    credit = ACH(amount=row["Amount"], fund=row["AccountName"][-5:], description=row["Description"], received=row["AsOfDate"], department_id=dep_id)
    db.session.add(credit)
    db.session.commit()

def process_ach(ach_file):
    with open(f'instance/ACH/{ach_file}', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if is_credit(row):
                categorize(row)
                   

