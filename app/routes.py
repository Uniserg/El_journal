from flask import render_template, flash, redirect, url_for, request
from app import app, db, get_group
from app.forms import *
from app.models import User, Grades, Schedule
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import time, datetime, timedelta
from sqlalchemy import and_


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('journal'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('journal'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.nick.data).first() or User.query.filter_by(phone=form.nick.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль')
            return  redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('Выполнен вход с пользователя ={}, запомпнить меня={}'.format(form.nick.data, form.remember_me.data))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('journal')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('journal'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, surname=form.surname.data,
                    patronymic=form.patronymic.data,
                    email=form.email.data, phone=form.phone.data)
        if form.generic_key.data:
            user.set_priority('Преподаватель')
            user.groups = dic[form.generic_key.data]
        else:
            user.groups = get_group()
            user.set_priority('Студент')

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем! Регистрация прошла успешно!')
        return redirect(url_for('login'))
    return render_template('sign up.html', title='Регистрация', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/journal')
@login_required
def journal():
    return render_template('journal.html', title='Журнал')


@app.route('/user/<name>_<surname>_id-<id>')
@login_required
def user(name, surname, id):
    user = User.query.filter_by(id=id).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts, title=f'{surname} {name}')


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.today()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Ваши изменения были сохранены.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    if current_user.priority == 'Преподаватель':
        now = datetime.now()
        g = set()
        zan = Schedule.query.filter(
            and_(Schedule.prepod_id == current_user.id,
                 now-timedelta(weeks=2) <= Schedule.date, Schedule.date <= now)).all()
        for i in zan:
            g.update(i.groups.split(', '))

        return render_template('groups.html', title='Группы', groups=sorted(g))
    else:
        return redirect(url_for('journal'))


@app.route('/grades/<group>', methods=['GET', 'POST'])
@login_required
def grades(group):
    if current_user.priority == 'Преподаватель':
        students_of_group = User.query.filter_by(groups=group).all()
        dz_now = None
        now = datetime.combine(datetime.now().date(), time(0, 0))
        dz = list(filter(lambda x: group in x.groups, Schedule.query.filter_by(prepod_id=current_user.id).filter(and_(now <= Schedule.date, Schedule.date < (now + timedelta(weeks=2)))).all()))
        if dz:
            dz_now = dz[0].dz
        zan = sorted(filter(lambda x: group in x.groups, Schedule.query.filter_by(prepod_id=current_user.id).all()), key=lambda x: x.date)
        d = dict(zip(map(lambda x: x.id, students_of_group),
                     (dict(zip(map(lambda x: x.date.date(), zan),
                               map(lambda x: {}, zan))) for _ in range(len(students_of_group)))))

        for i in students_of_group:
            for j in zan:
                d[i.id][j.date.date()][j.date.time()] = [j.id, None]

        for i in d:
            print(i, d[i])

        for i in zan:
            gr = i.grades.all()
            for j in gr:
                if j.user_id in d:
                    d[j.user_id][j.date][i.date.time()][1] = j.grade

        return render_template('grades.html', title='Список студентов', group=group, students=students_of_group, zan=zan, grades=d, dz_now=dz_now)
    else:
        return redirect(url_for('journal'))


@app.route('/get_dz', methods=['GET', 'POST'])
@login_required
def get_dz():
    dz = Schedule.query.filter_by(id=request.form['zan_id']).first()
    if 'input_dz' in request.form and request.form['input_dz']:
        dz.dz = request.form['input_dz']
        db.session.commit()
    return dz.dz if dz.dz else 'Пусто'


@app.route('/get_grade', methods=['GET', 'POST'])
@login_required
def get_grade():
    if current_user.priority == 'Преподаватель':
        date = datetime(*map(int, request.form['date'].split()[0].split('-'))).date()
        cur_student_id = int(request.form['student'])
        gr_rec = request.form['grade']
        zan = Schedule.query.filter_by(id=request.form['zan_id']).first()
        cur_grade = zan.grades.filter_by(user_id=cur_student_id, date=date, prepod=current_user.id).first()
        if request.form['summa']:
            summa = float(request.form['summa'])
        else:
            summa = 0
        comment = request.form['comment']

        if gr_rec:
            grade = Grades(user_id=cur_student_id,
                           prepod=current_user.id, grade=gr_rec, date=date, schedule=zan, comment=comment)
            if cur_grade:
                if cur_grade.grade != 'н':
                    summa -= float(cur_grade.grade)
                if grade.grade != 'н':
                    summa += float(grade.grade)
                cur_grade.grade = grade.grade
                cur_grade.comment = comment

            else:
                db.session.add(grade)
                db.session.commit()
                if grade.grade != 'н':
                    summa += float(grade.grade)
        else:
            if cur_grade:
                if cur_grade.grade != 'н':
                    summa -= float(cur_grade.grade)
                db.session.delete(cur_grade)
        db.session.commit()
        return str(round(summa, 3))
    else:
        return redirect(url_for('journal'))


def check_date(cur):
    return datetime.now().date() if cur == 'cur_week' else datetime(*map(int, cur.split()[0].split('-'))).date()


@app.route('/schedule_stud/<cur_week>', methods=['GET', 'POST'])
@login_required
def schedule_stud(cur_week):
    if current_user.priority == 'Студент':
        cur_week = check_date(cur_week)
        dates = cur_week - timedelta(days=cur_week.weekday())
        d = dict(zip(range(5),('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница')))
        list_zan = []
        for i in range(5):
            zan = filter(lambda x: current_user.groups in x.groups,
                                Schedule.query.filter(and_(dates < Schedule.date, Schedule.date < dates + timedelta(days=1))).order_by(Schedule.date).all())
            attr = [dates.strftime('%d.%m'), d[dates.weekday()]]
            for j in zan:
                prepod = User.query.filter_by(id=j.prepod_id).first()
                grade = j.grades.filter_by(user_id=current_user.id).first()
                comment = ''
                if grade:
                    comment = grade.comment
                    grade = grade.grade
                attr.append([prepod.groups, j.zan_type, f'{prepod.surname} {prepod.name} {prepod.patronymic}',
                             f'{j.date.time().strftime("%H:%M")} - {(j.date + timedelta(minutes=90)).time().strftime("%H:%M")}',
                             j.groups, j.dz, grade, comment])
            list_zan.append(attr)
            dates += timedelta(days=1)
        return render_template('schedule_stud.html', list_zan=list_zan, go_next=cur_week + timedelta(weeks=1), go_back=cur_week - timedelta(weeks=1))
    else:
        return redirect(url_for('journal'))


@app.route('/schedule_prepod/<cur_week>', methods=['GET', 'POST'])
@login_required
def schedule_prepod(cur_week):
    if current_user.priority == 'Преподаватель':
        cur_week = check_date(cur_week)
        dates = cur_week - timedelta(days=cur_week.weekday())
        d = dict(zip(range(5), ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница')))
        list_zan = []
        for i in range(5):
            zan = Schedule.query.filter_by(prepod_id=current_user.id).filter(
                and_(dates < Schedule.date, Schedule.date < dates + timedelta(days=1))).order_by(Schedule.date).all()
            attr = [dates.strftime('%d.%m'), d[dates.weekday()]]
            for j in zan:
                attr.append([j.zan_type, j.groups,
                             f'{j.date.time().strftime("%H:%M")} - {(j.date + timedelta(minutes=90)).time().strftime("%H:%M")}', j.dz if j.dz else 'Пусто'])
            list_zan.append(attr)
            dates += timedelta(days=1)
        return render_template('schedule_prepod.html', zan=list_zan, go_next=cur_week + timedelta(weeks=1), go_back=cur_week - timedelta(weeks=1))
    else:
        return redirect(url_for('journal'))