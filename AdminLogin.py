from flask_login import UserMixin


class UserLogin(UserMixin):
    def fromDB(self, admin_id, db):
        self.__admin = db.getUser(admin_id)
        return self

    def create(self, admin):
        self.__admin = admin
        return self

    def get_id(self):
        return str(self.__admin["id"])
