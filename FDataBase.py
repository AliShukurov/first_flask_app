"""
remembers the link to the database 
and returns a list to display in the menu
"""
import math, time, sqlite3, re
from flask import url_for


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = """SELECT * FROM mainmenu"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Ошибка чтения из Базы Данных")
        return []

    def addPost(self, title, text, url):
        try:
            self.__cur.execute(
                "SELECT COUNT() as `count` FROM posts WHERE url LIKE ?", (url,)
            )
            res = self.__cur.fetchone()
            if res["count"] > 0:
                print("Статья с таким url уже существует")
                return False

            base = url_for("static", filename="images_html")
            text = re.sub(
                r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                "\\g<tag>" + base + "/\\g<url>>",
                text,
            )

            tm = math.floor(time.time())
            self.__cur.execute(
                "INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)", (title, text, url, tm)
            )
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД " + str(e))
            return False

        return True

    def getPost(self, alias):
        try:
            self.__cur.execute(
                f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1"
            )
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute(
                f"SELECT id, title, text, url FROM posts ORDER BY time DESC"
            )
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return []

    # adding user data to the database

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(
                f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'"
            )
            res = self.__cur.fetchone()
            if res["count"] > 0:
                print("Пользователь с таким email уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute(
                "INSERT INTO users VALUES(NULL, ?, ?, ?, ?)", (name, email, hpsw, tm)
            )
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False

        return True

    # extract all fields for the specified id from the users table

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    # we extract data by user's email

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    # admin

    def getAdmin(self, admin_id):
        try:
            self.__cur.execute(f"SELECT * FROM admins WHERE id = {admin_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def UserFeedback(self, email, message):
        try:
            tm = math.floor(time.time())
            self.__cur.execute(
                "INSERT INTO feedbacks VALUES(NULL, ?, ?, ?)", (email, message, tm)
            )
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления отзыва в БД " + str(e))
            return False

        return True
