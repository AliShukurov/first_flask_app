from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    session,
    redirect,
    abort,
    g,
)
import sqlite3
import os
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm


# configuration
DATABASE = "/first_flask_app/flsite.db"
DEBUG = True
SECRET_KEY = "hfaiu89hdud7293jjdapwer9234"

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, "flsite.db")))


# enters information about the registered user into the session
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


# create database file
def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


# helper function for creating tables in a database
def create_db():
    db = connect_db()
    with app.open_resource("sq_db.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


# connecting with database if it don't connected
def get_db():
    if not hasattr(g, "link.db"):
        g.link_db = connect_db()
    return g.link_db


# closing the database connection
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "link_db"):
        g.link_db.close()


# connecting with database
dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


# main page


@app.route("/")
def index():
    return render_template(
        "index.html", menu=dbase.getMenu(), posts=dbase.getPostsAnonce()
    )


# about page


@app.route("/about")
def about():
    return render_template("about.html", menu=dbase.getMenu(), title="О сайте")


@app.route("/crupto")
def crupto():
    return render_template("crupto.html", menu=dbase.getMenu(), title="Цена Крипто")


# feedback page


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        if (
            len(request.form["username"]) > 2
            and len(request.form["message"]) > 8
            and "@" in request.form["email"]
        ):
            res = dbase.UserFeedback(request.form["email"], request.form["message"])
            if not res:
                flash("Ошибка оправки!", category="error")
            else:
                flash("Сообщение отправлено", category="success")
        else:
            flash("Заполните данные корректно.", category="error")
    return render_template("contact.html", menu=dbase.getMenu(), title="Обратная связь")


# add post page


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form["name"]) > 4 and len(request.form["post"]) > 10:
            res = dbase.addPost(
                request.form["name"], request.form["post"], request.form["url"]
            )
            if not res:
                flash("Ошибка добавления статьи", category="error")
            else:
                flash("Статья добавлена успешно", category="success")
        else:
            flash("Ошибка добавления статьи", category="error")

    return render_template(
        "add_post.html", menu=dbase.getMenu(), title="Добавление статьи"
    )


# show posts from the database


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template("post.html", menu=dbase.getMenu(), title=title, post=post)


# login and register pages


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user["psw"], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template(
        "login.html", menu=dbase.getMenu(), title="Авторизация", form=form
    )


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(request.form["psw"])
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for("login"))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template(
        "register.html", menu=dbase.getMenu(), title="Регистрация", form=form
    )


# profile page


@app.route("/profile")
@login_required
def profile():
    return f"""<a href="{url_for('logout')}">Выйти из профиля</a>
                user info: {current_user.get_id()}"""


# logout on profile page


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for("login"))


# error 404 page


@app.errorhandler(404)
def pageNotFount(error):
    return (
        render_template(
            "page404.html", title="Страница не найдена", menu=dbase.getMenu()
        ),
        404,
    )


if __name__ == "__main__":
    app.run(debug=True)
