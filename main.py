from flask import Flask
from data import db_session
from data.users import User

from forms import LoginForm, RegisterForm

import datetime

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import redirect, request, abort

from flask import render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/sputnik.db")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("index.html", text='Работай пж', title='Главная страница - Sputnic')


@app.route("/profile")
def profile():
    return render_template("profile.html", title='Профиль - Sputnic')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация - Sputnik', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User()
        if user and form.age.data and int(form.age.data) >= 14:
            user.name = form.name.data
            user.surname = form.surname.data
            user.age = form.age.data
            user.email = form.email.data
            user.password = form.password.data
            db_sess.add(user)
            db_sess.commit()
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('register.html',
                               message="Возраст не может быть меньше 14-ти",
                               form=form)
    return render_template('register.html', title='Регистрация - Sputnik', form=form)


@app.route("/none")
def none():
    return render_template("none.html",title='Ошибка 404 - Sputnic')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')