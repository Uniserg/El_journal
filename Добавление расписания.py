from app.models import Schedule, User
from app import db
from datetime import datetime, timedelta

n = 2
s = 'расписание ПИ19-'
for i in range(3, 6):
    f = open(s + str(i), encoding='utf-8')
    limit = datetime(2020, 6, 17)
    for i in f:
        a = i.strip().split('  ')
        a[5] = User.query.filter_by(surname=a[5], priority='Преподаватель').first()
        date = datetime(*map(int, (a[0], a[1], a[2], a[3], a[4])))
        while date < limit:
            zan = Schedule(date=date, prepod_id=a[5].id, groups=a[6], zan_type=a[7])
            db.session.add(zan)
            date += timedelta(weeks=int(a[8]))
    f.close()
db.session.commit()
