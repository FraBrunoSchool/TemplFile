import sqlite3


def validate(username, password):
    db_connection = sqlite3.connect('static/TemplFile.db')
    db_cursor = db_connection.cursor()

    lista_iscritti = []
    for row in db_cursor.execute(
        f'SELECT username, password FROM Users WHERE username="{username}"'): lista_iscritti.append((row[0], row[1]))
    print(lista_iscritti)
    for iscritto in lista_iscritti:
        if username == iscritto[0] and password == iscritto[1]:
            print(f"Username: {username} - Password: {password} -> FOUND")
            return True
    print(f"Username: {username} - Password: {password} -> NOT FOUND")
    return False


if __name__ == '__main__':
    print(validate("test", "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"))
