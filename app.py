from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
import config
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(config.Config)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_MODIFICATIONS'] = False
db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Fname = db.Column(db.String(30), nullable=False)
    Lname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


with app.app_context():
    db.create_all()


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    intro = db.Column(db.String(100))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Notes %r>' % self.id


with app.app_context():
    db.create_all()


@app.route('/', methods=['POST', 'GET'])  # вход/регистрация
def entrance_registration():
    if request.method == 'POST':
        try:                                                                # login form
            email = request.form['email_log']
            password = request.form['password_log']
            user = User(email=email, password=password)
            try:
                email_username = user.query.filter_by(email=email).first()
                Password = user.query.filter_by(password=password).first()
                if not email_username:
                    return render_template("/entrance_registration.html", error_login="Такого пользователя не существует!")
                elif email_username and not Password:
                    return render_template("/entrance_registration.html", error_login="Неверный пароль!")
                else:
                    return redirect('/dashboard')
            except:
                return "Ошибка входа"
        except:                                                             # registration form
            Fname = request.form['Fname_reg']
            Lname = request.form['Lname_reg']
            email = request.form['email_reg']
            password = request.form['password_reg']
            password_check = request.form['password_check_reg']
            if password != password_check:
                return render_template("/entrance_registration.html", error_register="Пароли не совпадают!", error_register_trigger="active")
            else:
                user = User(email=email, Fname=Fname, Lname=Lname, password=password)
                try:
                    Email = user.query.filter_by(email=email).first()
                    if Email:
                        return render_template("/entrance_registration.html", error_register="Пользователь с такой почтой уже существует!", error_register_trigger="active")
                    else:
                        db.session.add(user)
                        db.session.commit()
                        return redirect('/')
                except:
                    return "Ошибка регистрации"
    else:
        return render_template("/entrance_registration.html")


@app.route('/dashboard')
def dashboard():
    notes = Notes.query.order_by(Notes.date.desc()).all()
    return render_template("main/dashboard/dashboard.html", notes=notes)


@app.route('/create_notes', methods=['POST', 'GET'])  # создать заметку
def create_notes():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        notes = Notes(title=title, intro=intro, text=text)
        try:
            db.session.add(notes)
            db.session.commit()
            return redirect('/dashboard')
        except:
            return "При добавлении заметки произошла ошибка"
    else:
        return render_template("main/dashboard/notes/create_notes.html")


@app.route('/dashboard/<int:id>/detail')  # детальнее о заметке (показать текст)
def notes_detail(id):
    notes = Notes.query.get(id)
    return render_template("main/dashboard/notes/notes_detail.html", notes=notes)


@app.route('/dashboard/<int:id>/update', methods=['POST', 'GET'])  # редактировать заметку
def notes_update(id):
    notes = Notes.query.get(id)
    if request.method == 'POST':
        notes.title = request.form['title']
        notes.intro = request.form['intro']
        notes.text = request.form['text']
        try:
            db.session.commit()
            return redirect('/dashboard')
        except:
            return
    else:
        return render_template("main/dashboard/notes/notes_update.html", notes=notes)


@app.route('/dashboard/<int:id>/delete')  # удалить заметку
def notes_delete(id):
    notes = Notes.query.get_or_404(id)
    try:
        db.session.delete(notes)
        db.session.commit()
        return redirect('/dashboard')
    except:
        return "При удалении статьи произошла ошибка"


@app.route('/curses')
def curses():
    return render_template("main/curses/curses.html")


@app.route('/personal_account')
def personal_account():
    user = User.query.all()
    return render_template("main/personal_account/personal_account.html", user=user)


@app.route('/schedule')
def schedule():
    return render_template("main/schedule/schedule.html")


if __name__ == "__main__":
    app.run(debug=True)
