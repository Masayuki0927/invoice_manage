# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime


# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)  # ユーザーID
#     username = db.Column(db.String(80), unique=True, nullable=True)
#     email_address = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=False)
#     companies = db.relationship('Company', backref='User', lazy=True) # 1対多の関係を定義

#     # パスワードをハッシュ化して保存
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
#     # パスワードが正しいかチェック
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
    
# class Company(db.Model):
#     __tablename__ = 'companies'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), nullable=False)
#     duedate = db.Column(db.DateTime, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 外部キー
#     invoices = db.relationship('Invoice', backref='Company', lazy=True) 

# class Invoice(db.Model):
#     __tablename__ = 'invoices'
#     id = db.Column(db.Integer, primary_key=True)
#     period = db.Column(db.Date, nullable=False)
#     status = db.Column(db.String, nullable=False)
#     company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
#     sendemails = db.relationship('SendEmail', backref='Invoice', lazy=True)

# class SendEmail(db.Model):
#     __tablename__ = 'sendemails'
#     id = db.Column(db.Integer, primary_key=True)
#     email_address = db.Column(db.String(120), nullable=False)
#     title = db.Column(db.String(120), nullable=False)
#     body = db.Column(db.Text, nullable=False)
#     senddate = db.Column(db.DateTime, nullable=False)
#     invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)