import hashlib
import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

FILE_FOLDER = 'static/FILE_FOLDER'
app = Flask(__name__)
app.config['FILE_FOLDER'] = FILE_FOLDER
app.secret_key = 'TemplFile'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/founders')
def founders():
    return render_template('founders.html')


@app.route('/categorie')
def categorie():
    return render_template('categorie.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    db_connection = sqlite3.connect('static/TemplFile.db')
    db_cursor = db_connection.cursor()
    data = []
    for row in db_cursor.execute(f'SELECT categoria FROM Categorie'): data.append({'name': row[0]})
    db_cursor.close()
    print(data)
    db_connection = sqlite3.connect('static/TemplFile.db')
    db_cursor = db_connection.cursor()
    url = []
    for row in db_cursor.execute(f'SELECT nome_file FROM File WHERE username_utente = "{session["username"]}"'):
        url.append({'username': session['username'], 'file_name': row[0]})
    db_cursor.close()

    # return render_template('user_page.html', user=session['username'], lista_categorie=data, lista_url=url, search=session['url_search'])
    return render_template('user_page_test.html', user=session['username'], lista_url=url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    session['url_search'] = [{'username': ' ', 'file_name': 'nessuna ricerca effettuata'}]
    error = None
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']
        session['username'] = username
        password = (hashlib.sha256(bytes(f"{password}", "utf-8"))).hexdigest()
        val_ok = validate(username, password)
        if not val_ok:
            error = "Credenziali non valide"
            print(f"Username: {username} - Password: {password} -> Login Fallito")
        else:
            print(f"Username: {username} - Password: {password} -> Login Ok")
            return redirect(url_for('user_page'))
    return render_template('login.html', error=error)


def validate(username, password):
    db_connection = sqlite3.connect('static/TemplFile.db')
    db_cursor = db_connection.cursor()

    lista_iscritti = []
    for row in db_cursor.execute(
            f'SELECT username, password FROM Users WHERE username="{username}"'): lista_iscritti.append(
        (row[0], row[1]))
    db_connection.close()
    print(lista_iscritti)
    for iscritto in lista_iscritti:
        if username == iscritto[0] and password == iscritto[1]:
            print(f"Username: {username} - Password: {password} -> FOUND")
            return True
    print(f"Username: {username} - Password: {password} -> NOT FOUND")
    return False


@app.route('/uploader', methods=['POST'])
def upload_file():
    f = request.files['file']
    categoria = request.form['categoria']
    filename = secure_filename(f.filename)
    username = session['username']
    f.save(os.path.join(app.config['FILE_FOLDER'] + f"/{username}", filename))
    db_connection = sqlite3.connect('static/TemplFile.db')
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        f"INSERT INTO File ('nome_file','categoria_file','username_utente') VALUES ('{filename}','{categoria}','{username}')")
    db_cursor.execute("COMMIT;")
    db_cursor.close()
    return redirect(url_for('user_page'))


@app.route('/search', methods=['POST'])
def search_file():
    search = request.form['search']
    # username = session['username']
    db_connection = sqlite3.connect('static/TemplFile.db')
    db_cursor = db_connection.cursor()
    nome_file = []
    nome_utenti = []
    for row in db_cursor.execute("SELECT nome_file, username_utente FROM File"):
        nome_file.append(row[0])
        nome_utenti.append(row[1])
    url = []
    for index, el in enumerate(nome_file):
        if search in nome_file:
            url.append({'username': nome_utenti[index], 'file_name': el})
    db_cursor.close()
    session['url_search'] = url
    return redirect(url_for('user_page'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    print(request)
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']
        name = request.form['Name']
        surname = request.form['Surname']
        email = request.form['Email']
        password = (hashlib.sha256(bytes(f"{password}", "utf-8"))).hexdigest()
        print(password)

        if username_free(username):
            insert_user(username, password, name, surname, email)
            # Parent Directory path
            parent_dir = "D:\Dati\Desktop\GitHub\TemplFile\static\FILE_FOLDER"
            # Path
            path = os.path.join(parent_dir, username)
            os.mkdir(path)
            return redirect(url_for('login'))
        else:
            error = "Username già in uso"

    return render_template('signup.html', error=error)


def username_free(username):
    db_connection = sqlite3.connect('static/TemplFile.db')
    db_cursor = db_connection.cursor()
    lista_username = []
    for row in db_cursor.execute(
            'SELECT username FROM Users'): lista_username.append(row[0])
    db_cursor.close()
    if username in lista_username:
        return False
    else:
        return True


def insert_user(username, password, name, surname, email):
    print("insert user")
    db_connection = sqlite3.connect('static/TemplFile.db')
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        f"INSERT INTO Users ('username','nome','cognome', 'email','password') VALUES ('{username}','{name}','{surname}', '{email}','{password}')")
    db_cursor.execute("COMMIT;")
    db_cursor.close()


if __name__ == '__main__':
    app.run(host='192.168.0.30', debug='on')
