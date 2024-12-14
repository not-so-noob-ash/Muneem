from Muneem import db
import datetime

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=100), nullable=False, unique=True)
    email_address = db.Column(db.String(length=100), nullable=False, unique= True)
    password_hash= db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Float(),nullable=False)
    preffered_currency = db.Column(db.String(length=10), nullable=False)
    prs_expenses  = db.relationship('Personal_Expense', backref = 'owned_user', lazy=True)
class Personal_Expense(db.Model):
    __tablename__ = 'personal_expense'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(length=100), nullable=False)
    category = db.Column(db.String(length=30),nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)
    amount = db.Column(db.Float(),nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))



class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to the first user
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to the second user
    user = db.relationship('User', foreign_keys=[user_id], backref='friends_with_me', lazy=True)
    friend = db.relationship('User', foreign_keys=[friend_id], backref='friends_of_me', lazy=True)



class SplitExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('personal_expense.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
