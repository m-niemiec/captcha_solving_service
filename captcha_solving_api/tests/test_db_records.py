import pytest
from fastapi_sqlalchemy import db

from models import User as ModelUser, CreditsTransaction as ModelCreditsTransaction, \
    CaptchaSolveQuery as ModelCaptchaSolveQuery


@pytest.mark.order(7)
def test_users_amount():
    with db():
        users = db.session.query(ModelUser).all()

        assert len(users) == 3


@pytest.mark.run(after='test_users_amount')
def test_utility_users_ids():
    with db():
        admin_user = db.session.query(ModelUser).filter(ModelUser.username == 'admin').first()
        test_user = db.session.query(ModelUser).filter(ModelUser.username == 'test').first()
        pytest_user = db.session.query(ModelUser).filter(ModelUser.username == 'pytest').first()

        assert admin_user.id == 1
        assert test_user.id == 2
        assert pytest_user.id == 3


@pytest.mark.run(after='test_users_amount')
def test_captcha_solve_query():
    with db():
        captcha_solve_query = db.session.query(ModelCaptchaSolveQuery).all()

        assert len(captcha_solve_query) == 6


@pytest.mark.run(after='test_users_amount')
def test_credits_transaction_query():
    with db():
        credits_transaction_query = db.session.query(ModelCreditsTransaction).all()

        assert len(credits_transaction_query) == 2


@pytest.mark.run(after='test_users_amount')
def test_users_credit_balance():
    with db():
        admin_user = db.session.query(ModelUser).filter(ModelUser.username == 'admin').first()
        test_user = db.session.query(ModelUser).filter(ModelUser.username == 'test').first()
        pytest_user = db.session.query(ModelUser).filter(ModelUser.username == 'pytest').first()

        assert admin_user.credit_balance == 999999
        assert test_user.credit_balance == 999999
        assert pytest_user.credit_balance == 0
