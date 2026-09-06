from config.database import db
from models.users import User
from sqlalchemy.exc import IntegrityError


class UserDAO:

    # pagination information
    # pagination.has_next
    # pagination.has_prev

    def get_all(self, page, per_page):
        return User.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, user_id):
        return User.query.get(user_id)

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def save_user(self, user):
        db.session.add(user)
        db.session.commit()
        return user

    def update(self, user):
        db.session.commit()
        return user

    def delete(self, user):
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False
