from app.models import User, generate_password_hash
from app import db

f = open('Преподаватели', encoding='utf-8')
for i in f:
    a = i.strip().split(', ')
    print(a)
    user = User(surname=a[0], name=a[1], patronymic=a[2], groups=a[3],
                email=a[4], password_hash=generate_password_hash(a[5]),
                priority='Преподаватель')

    db.session.add(user)
f.close()
db.session.commit()
