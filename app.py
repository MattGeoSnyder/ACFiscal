from flask import Flask, g, render_template, redirect, session, flash, request, send_from_directory
from forms import ACH_Credits_Form, ROC_Form, SignupForm, LoginForm, UnclaimedCredits, AllCredits
from secret import app_secret_key
from flask_debugtoolbar import DebugToolbarExtension
from ach import process_ach
from models import db, connect_db, ACH, ROC, SupportingDoc, User, Department
import os
import pdb
from datetime import date, datetime
from urllib.parse import urlparse, parse_qs
import json
import requests

USER_KEY = "curr_user"

app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = app_secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ACFiscal'
app.config['SQLALCHEMY_ECHO'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)

with app.app_context():
    db.create_all()


@app.before_request
def add_user_to_g():

    if USER_KEY in session:
        g.user = User.query.get(session[USER_KEY])
    else:
        g.user = None


def do_login(user):
    session[USER_KEY] = user.id


def do_logout():
    if USER_KEY in session:
        del session[USER_KEY]


@app.route('/api/search')
def query_ach_credits():
    q = ACH.query.outerjoin(ACH.department).outerjoin(ACH.roc)

    qs = urlparse(request.url).query
    params = parse_qs(qs, keep_blank_values=True)
    claimed = params.get('claimed', [''])[0]
    selected = json.loads(params.get('selected', ['[]'])[0])
    rec_start_date = params.get('rec_start_date', [''])[0]
    rec_end_date = params.get('rec_end_date', [''])[0]
    clm_start_date = params.get('clm_start_date', [''])[0]
    clm_end_date = params.get('clm_end_date', [''])[0]
    book_start_date = params.get('book_start_date', [''])[0]
    book_end_date = params.get('book_end_date', [''])[0]
    department = params.get('department', [''])[0]
    bank = params.get('bank', [''])[0]
    amount = params.get('amount', [''])[0]
    ret = []

    if not claimed:
        q = q.filter(ACH.roc_id == None)
    if rec_start_date:
        rec_start_date = datetime.strptime(rec_start_date, '%Y-%m-%d')
        q = q.filter(ACH.received >= rec_start_date)
    if rec_end_date:
        rec_end_date = datetime.strptime(rec_end_date, '%Y-%m-%d')
        q = q.filter(ACH.received <= rec_end_date)
    if clm_start_date:
        clm_start_date = datetime.strptime(clm_start_date, '%Y-%m-%d')
        q = q.filter(ROC.claimed >= clm_start_date)
    if clm_end_date:
        clm_end_date = datetime.strptime(clm_end_date, '%Y-%m-%d')
        q = q.filter(ROC.claimed <= clm_end_date)
    if book_start_date:
        book_start_date = datetime.strptime(book_start_date, '%Y-%m-%d')
        q = q.filter(ROC.booked >= book_start_date)
    if book_end_date:
        book_end_date = datetime.strptime(book_end_date, '%Y-%m-%d')
        q = q.filter(ROC.booked <= book_end_date)
    if department:
        dep_id = int(department)
        q = q.filter(Department.id == dep_id)
    if bank:
        q = q.filter(ACH.fund == bank)
    if amount:
        lower_bound = float(params['amount'][0])
        upper_bound = lower_bound + 0.009
        q = q.filter(ACH.amount >= lower_bound)
        q = q.filter(ACH.amount <= upper_bound)
    if selected:
        q = q.filter(ACH.id.not_in(selected))

    q = q.order_by(ACH.received.desc(), ACH.fund.desc(),
                   ACH.amount.desc(), Department.name)

    if claimed:
        q = q.limit(50)
    for credit in q.all():
        cred_dict = {
            'id': credit.id,
            'received': credit.received.strftime('%m/%d/%Y'),
            'department': credit.department.name if credit.department else 'Unidentified',
            'claimed': credit.roc.claimed.strftime('%m/%d/%Y') if credit.roc else 'Unclaimed',
            'bank': credit.fund,
            'amount': '${:,.2f}'.format(credit.amount),
            'description': credit.description,
            'roc': {'id': credit.roc.id if credit.roc else '',
                    'filename': credit.roc.filename if credit.roc else ''
                    }
        }
        if credit.roc:
            cred_dict['booked'] = credit.roc.booked.strftime(
                '%m/%d/%Y') if credit.roc.booked else 'Unbooked'
        else:
            cred_dict['booked'] = 'Unbooked'
        ret.append(cred_dict)
    return json.dumps({'credits': ret})


@app.route('/')
def go_to_fiscal():
    return redirect('/signup')


@app.route('/fiscal')
def get_homepage():
    return redirect('/fiscal/ACH')


@app.route('/fiscal/ACH')
def list_ach_credits():
    search_form = UnclaimedCredits()
    search_form.department.choices = [
        (dep.id, dep.name) for dep in Department.query.order_by(Department.name)]
    search_form.department.choices.insert(0, ("", 'All'))
    # q = query_unclaimed_ach_credits(params)
    # ach_credits = q.order_by(ACH.received, ACH.fund.desc(), ACH.amount.desc(), Department.name).all()

    return render_template('ACH.html', search_form=search_form)


@app.route('/fiscal/ACH/add', methods=['GET', 'POST'])
def add_ach_credits():
    form = ACH_Credits_Form()
    if form.validate_on_submit():
        file_data = form.file.data
        filename = file_data.filename
        file_data.save(os.path.join(app.instance_path, 'ACH', filename))
        process_ach(filename)
        return redirect('/fiscal/ACH')

    return render_template('ACH-add.html', form=form)


@app.route('/fiscal/ACH/claim', methods=['POST'])
def claim_ach_credits():
    form = ROC_Form()
    claimed_credits = request.form.getlist('credit-id')
    credit_ids = [int(credit) for credit in claimed_credits]
    ach_credits = ACH.query.filter(ACH.id.in_(credit_ids)).all()
    total = 0
    for credit in ach_credits:
        total += credit.amount

    if form.validate_on_submit():

        # pdb.set_trace()
        roc_data = form.roc.data.read()
        roc_filename = form.roc.data.filename
        roc_amount = float(request.form['amount'])
        roc = ROC(roc=roc_data, filename=roc_filename,
                  claimed=date.today(), amount=roc_amount)
        roc.user = g.user
        db.session.add(roc)

        claimed_credits = request.form.getlist('credit-id')
        credit_ids = [int(credit) for credit in claimed_credits]
        ach_credits = ACH.query.filter(ACH.id.in_(credit_ids)).all()

        for credit in ach_credits:
            credit.roc = roc

        # pdb.set_trace()
        if form.supporting_docs.data[0].filename:
            for file_data in form.supporting_docs.data:
                doc_data = file_data.read()
                doc_name = file_data.filename
                doc = SupportingDoc(doc=doc_data, filename=doc_name)
                doc.roc = roc
                db.session.add(doc)

        db.session.commit()
        return redirect('/fiscal/ACH')

    return render_template('ACH-claim.html', form=form, ach_credits=ach_credits, total=total)


@app.route('/fiscal/ACH/book')
def book_ach_credits():
    rocs = ROC.query.filter(ROC.booked == None).order_by(
        ROC.claimed.desc()).all()
    # pdb.set_trace()
    return render_template('ACH-book.html', rocs=rocs)


@app.route('/fiscal/ACH/book/<int:roc_id>')
def get_roc(roc_id):
    roc = ROC.query.get_or_404(roc_id)
    data = roc.roc
    path = os.path.join(app.instance_path, 'ROC', roc.filename)
    f = open(path, "wb")
    f.write(data)
    f.close()
    if roc.docs:
        for doc in roc.docs:
            path = os.path.join(app.instance_path,
                                'SupportingDocs', doc.filename)
            data = doc.doc
            f = open(path, "wb")
            f.write(data)
            f.close()
    return render_template('ROC.html', roc=roc, path=path)


@app.route('/fiscal/ACH/book/<int:roc_id>', methods=['POST'])
def book_roc(roc_id):
    roc = ROC.query.get_or_404(roc_id)
    roc.booked = datetime.today()
    db.session.commit()
    return redirect('/fiscal/ACH/book')


@app.route('/instance/ROC/<path:filename>')
def download_file(filename):
    path = os.path.join(app.root_path, 'instance/ROC')
    return send_from_directory(path, filename, as_attachment=True)


@app.route('/instance/SupportingDocs/<path:filename>')
def download_doc(filename):
    path = os.path.join(app.root_path, 'instance/SupportingDocs')
    return send_from_directory(path, filename, as_attachment=True)


@app.route('/fiscal/ACH/recon')
def recon():
    form = AllCredits()
    form.department.choices = [
        (dep.id, dep.name) for dep in Department.query.order_by(Department.name).all()]
    form.department.choices.insert(0, ("", "All"))
    return render_template('ACH-recon.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    form.department.choices = [(dep.id, dep.name)
                               for dep in Department.query.order_by(Department.name)]
    if form.validate_on_submit():
        user = User.signup(form.first_name.data,
                           form.last_name.data,
                           form.email.data.lower(),
                           form.password.data,
                           form.department.data)
        db.session.add(user)
        db.session.commit()
        do_login(user)
        return redirect('/fiscal/ACH')
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if g.user:
            do_logout()

        user = User.authenticate(form.email.data.lower(), form.password.data)

        if user:
            do_login(user)
            return redirect('/fiscal/ACH')

        # flash message here

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():

    do_logout()

    return redirect('/login')
