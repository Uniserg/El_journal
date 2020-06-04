from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import random

list_groups = 'ПИ19-1', 'ПИ19-2', 'ПИ19-3', 'ПИ19-4', 'ПИ19-5'


def get_group():
    return random.choice(list_groups)


def generic_keys():
    n = 12
    s = ''
    for _ in range(n):
        s += chr(random.randint(33,126))
    return s


keys = set()
dic = {}
subjects = 'Математика', 'Алгоритмы и структуры данных', 'Алгоритмы и структуры данных', 'ОВС'
for i in range(4):
    new_key = generic_keys()
    while new_key in dic:
        new_key = generic_keys()
    dic[new_key] = subjects[i]

print(dic)
app = Flask(__name__)
gk = generic_keys()
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models, errors