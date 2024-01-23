from flask import Flask, render_template, request, session, redirect, url_for
# from models.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # SQLiteデータベースのファイル名
app.config['SECRET_KEY'] = secrets.token_hex(16) 
app.permanent_session_lifetime = timedelta(days=1) # セッションの有効期限を1日に設定
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # ユーザーID
    username = db.Column(db.String(80), unique=True, nullable=True)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    companies = db.relationship('Company', backref='User', lazy=True) # 1対多の関係を定義

    # パスワードをハッシュ化して保存
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    # パスワードが正しいかチェック
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    duedate = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 外部キー
    invoices = db.relationship('Invoice', backref='Company', lazy=True) 

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Date, nullable=False)
    status = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    sendemails = db.relationship('SendEmail', backref='Invoice', lazy=True)

class SendEmail(db.Model):
    __tablename__ = 'sendemails'
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    senddate = db.Column(db.DateTime, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/signup', methods=["GET"])
def show_signup_form():
    return render_template('signup.html')

@app.route('/signup' , methods=["post"])
def signup():
    email_address = request.form.get('email_address')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password == confirm_password:
        password_hash = generate_password_hash(password)
        new_user = User(email_address=email_address, password_hash = password_hash)
        db.session.add(new_user)
        db.session.commit()
        session['email_address'] = email_address
        return render_template("company.html")

@app.route('/login' , methods=["post"])
def login():
    email_address = request.form.get('email_address')
    password = request.form.get('password')
    user = User.query.filter_by(email_address=email_address).first()
    if user and check_password_hash(user.password_hash, password):
        session['email_address'] = email_address
        companies = user.companies
        # return render_template('company.html', companies=companies)
        return redirect(url_for('show_company'))
    else:
        return 'Invalid email_address or password'

@app.route('/logout')
def logout():
    session.pop('email_address', None)  # セッションからユーザー名を削除
    return redirect(url_for('home'))

@app.route('/company', methods=["GET"])
def show_company():
    if 'email_address' in session and session['email_address'] is not None:
        user_id = User.query.filter_by(email_address=session['email_address']).first().id
        companies = Company.query.filter_by(user_id=user_id).all()
        return render_template('company.html', companies=companies)
    else:
        return redirect(url_for('home'))

@app.route('/company_create', methods=["GET"])
def show_company_create():
    return render_template('company_create.html')

@app.route('/company_create', methods=["post"])
def company_create():
    name = request.form.get('name')
    duedate = request.form.get('duedate')
    user_id = User.query.filter_by(email_address=session['email_address']).first().id
    new_company = Company(name=name, duedate=duedate, user_id=user_id)
    db.session.add(new_company)
    db.session.commit()
    companies = Company.query.filter_by(user_id=user_id).all()
    # return render_template('company.html', companies=companies)
    return redirect(url_for('show_company'))

@app.route('/company_edit/<int:company_id>', methods=['GET'])
def show_company_edit(company_id):
    company_edit = Company.query.get(company_id)
    return render_template('company_edit.html', company=company_edit)

@app.route('/company_edit/<int:company_id>', methods=['POST'])
def company_edit(company_id):
    company_edit = Company.query.get(company_id)
    company_edit.name = request.form.get('name')
    company_edit.duedate = request.form.get('duedate')
    db.session.commit()
    return redirect(url_for('show_company'))


@app.route('/invoice_home/<int:company_id>', methods=["GET"])
def invoice_home(company_id):
    company = Company.query.get(company_id)
    invoices = Invoice.query.filter_by(company_id=company_id).all()
    return render_template('invoice.html', invoices=invoices, company = company)

@app.route('/invoice_create/<int:company_id>', methods=["GET"])
def show_invoice_create(company_id):
    company = Company.query.get(company_id)
    return render_template('invoice_create.html', company = company)

@app.route('/invoice_create/<int:company_id>', methods=["post"])
def invoice_create(company_id):
    period = request.form.get('period')
    period_date = datetime.strptime(period, '%Y-%m-%d').date()
    status = '未送信'
    new_invoice = Invoice(period=period_date, status=status, company_id=company_id)
    db.session.add(new_invoice)
    db.session.commit()
    return redirect(url_for('invoice_home', company_id=company_id))


if __name__ == "__main__":
    app.run(debug=True)
