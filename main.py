import sqlalchemy
from flask import Flask
from data import db_session
from data.users import User
from data.news import News
from data.arts import Arts
from PIL import Image

from forms import LoginForm, RegisterForm, ContentForm

import datetime

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import redirect, request, abort

from flask import render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/sputnik.db")


def verifyext(filename):
    ext = filename.rsplit('.', 1)[1]
    if ext == "png" or ext == "PNG" or ext == "jpg" or ext == "JPG":
        return True
    return False


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()
    articles = db_sess.query(Arts).all()
    return render_template("index.html", news=news, articles=articles, title='Главная страница - Sputnic')


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


@app.route('/art/<int:id>')
@login_required
def art(id):
    db_sess = db_session.create_session()
    art = db_sess.query(Arts).filter(Arts.id == id).first()
    return render_template('art.html', title=f'{art.title} - Sputnik', art=art)


@app.route('/add_art', methods=['GET', 'POST'])
@login_required
def add_art():
    form = ContentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        all_art = db_sess.query(Arts).all()
        le = len(all_art)
        art = Arts()
        art.title = form.title.data
        art.content = form.content.data
        art.picture = ''
        current_user.arts.append(art)
        img = Image.open(form.picture.data)
        img.save(f'static/img/articles/back_art{le}.png')
        art.picture = f'back_art{le}.png'
        db_sess.merge(current_user)
        db_sess.commit()
        db_sess.close()

        return redirect('/')
    return render_template('content.html', title='Новая статья - Sputnik', form=form)


@app.route("/none")
def none():
    return render_template("none.html",title='Ошибка 404 - Sputnic')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')