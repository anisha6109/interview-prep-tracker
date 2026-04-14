from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    points = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.Date, nullable=True)

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), default='Unsolved')
    date_solved = db.Column(db.DateTime, default=datetime.utcnow)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(100), nullable=False)

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    questions = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=True)
    tips = db.Column(db.Text, nullable=True)
