from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String(64))
    surname = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True)
    patronymic = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.Integer, index=True, unique=True)
    groups = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.today)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=mp&s={}'.format(digest, size)

    def __repr__(self):
        return '<User {}, {}, {}, {}, {}, {}, {}, {}, {}>'.format(self.id, self.priority, self.name, self.surname, self.email, self.phone, self.groups, self.about_me, self.last_seen)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_priority(self, pr):
        self.priority = pr

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))


class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    user_id = db.Column(db.Integer, index=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    prepod = db.Column(db.Integer, index=True)
    grade = db.Column(db.Integer)
    comment = db.Column(db.Integer)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True)
    prepod_id = db.Column(db.Integer, index=True)
    zan_type = db.Column(db.String(12), index=True)
    groups = db.Column(db.String(10), index=True)
    dz = db.Column(db.String(140))
    grades = db.relationship('Grades', backref='schedule', lazy='dynamic')

    def __repr__(self):
        return '{}, {}'.format(self.date, self.prepod_id)


