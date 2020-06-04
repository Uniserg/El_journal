from app.models import User, generate_password_hash
from app import db

s = 'ПИ19-'
mail = 'exPI19_'
for i in range(1, 6):
    group = s + str(i)
    f = open(group, encoding='utf-8')
    k = 0
    for j in f:
        fio = j.strip().split()
        email = mail + str(i) + '_' + str(k+1) + '@mail.ru'
        password = generate_password_hash('12345')
        priority = 'Студент'
        user = User(surname=fio[0], name=fio[1], patronymic=fio[2], groups=group,
                    email=email, password_hash=password, priority=priority)
        db.session.add(user)
        k += 1
    f.close()
db.session.commit()
