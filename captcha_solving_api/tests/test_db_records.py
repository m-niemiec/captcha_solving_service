from fastapi_sqlalchemy import db

from models import User as ModelUser, CreditsTransaction as ModelCreditsTransaction, \
    CaptchaSolveQuery as ModelCaptchaSolveQuery


def test_users_amount(add_user_response):
    with db():
        users = db.session.query(ModelUser).all()

        assert len(users) == 3


def test_utility_users_ids(add_user_response):
    with db():
        admin_user = db.session.query(ModelUser).filter(ModelUser.username == 'admin').first()
        test_user = db.session.query(ModelUser).filter(ModelUser.username == 'test').first()
        pytest_user = db.session.query(ModelUser).filter(ModelUser.username == 'pytest').first()

        assert admin_user.id == 1
        assert test_user.id == 2
        assert pytest_user.id == 3


def test_captcha_solve_query(upload_captcha: tuple[str, str, int]):
    task_index = upload_captcha[2]

    with db():
        captcha_solve_query = db.session.query(ModelCaptchaSolveQuery).all()

        assert len(captcha_solve_query) == task_index


def test_credits_transaction_query(add_credit_balance, reduce_credit_balance):
    with db():
        credits_transaction_query = db.session.query(ModelCreditsTransaction).all()

        assert len(credits_transaction_query) == 2


def test_users_credit_balance(add_user_response, add_credit_balance, reduce_credit_balance,
                              upload_captcha: tuple[str, str, int]):
    task_index = upload_captcha[2]

    with db():
        admin_user = db.session.query(ModelUser).filter(ModelUser.username == 'admin').first()
        test_user = db.session.query(ModelUser).filter(ModelUser.username == 'test').first()
        pytest_user = db.session.query(ModelUser).filter(ModelUser.username == 'pytest').first()

        assert admin_user.credit_balance == 999999
        assert test_user.credit_balance == 999999 - task_index
        assert pytest_user.credit_balance == 0
