from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
from app import dic


class EditProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    about_me = TextAreaField('О себе:', validators=[Length(min=0, max=140)])
    submit = SubmitField('Принять')


class SignupForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    generic_key = PasswordField('Ключ преподавателя')
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Зарегистрироваться')

    def validate_phonenumber(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user is not None:
            raise ValidationError('Пользователь с данным номером телефона уже зарегистрирован.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пользователь с данным email уже зарегистрирован.')

    def validate_generic_key(self, generic_key):
        if generic_key.data and generic_key.data not in dic:
            raise ValidationError('Неверный ключ преподавателя.')


class LoginForm(FlaskForm):
    nick = StringField('Телефон/email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class HomeAss(FlaskForm):
    data = TextAreaField(validators=[Length(min=0, max=140)])
    submit = SubmitField('Принять')
