from fastapi_sqlalchemy import db

from manage_authorizations import ManageAuthorization
from models import User as ModelUser


def add_preview_users():
    # Add admin user with user id - 1
    hashed_password = ManageAuthorization().get_password_hash('admin')

    user_db = ModelUser(username='admin',
                        email='admin@admin.com',
                        credit_balance=999999,
                        password=hashed_password)
    db.session.add(user_db)
    db.session.commit()

    # Add test user
    hashed_password = ManageAuthorization().get_password_hash('test')

    user_db = ModelUser(username='test',
                        email='test@test.com',
                        credit_balance=999999,
                        password=hashed_password)
    db.session.add(user_db)
    db.session.commit()