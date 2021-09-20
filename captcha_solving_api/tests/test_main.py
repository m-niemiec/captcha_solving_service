import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi_sqlalchemy import db
from main import app
from models import Base

from models import User as ModelUser, CreditsTransaction as ModelCreditsTransaction, \
    CaptchaSolveQuery as ModelCaptchaSolveQuery

client = TestClient(app)
engine = create_engine(os.environ['DATABASE_URL'], connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def test_add_user(add_user):
    assert add_user.status_code == 200
    assert 'username' in add_user.json() and add_user.json().get('username') == 'pytest'
    assert 'email' in add_user.json() and add_user.json().get('email') == 'pytest@pytest'
    assert 'password' in add_user.json() and add_user.json().get('password') != 'pytest' and \
           len(add_user.json().get('password')) == 60


def test_get_account_info(add_user, add_credit_balance, reduce_credit_balance):
    response = client.post('/get_account_info',
                           headers={'Authorization': f'Bearer {test_get_token("pytest", "pytest")}'})

    assert response.status_code == 200
    assert 'account_info' in response.json()

    account_info = response.json()['account_info']

    assert 'id' in account_info and account_info.get('id') == 3
    assert 'credit_balance' in account_info and account_info.get('credit_balance') == 0
    assert 'username' in account_info and account_info.get('username') == 'pytest'
    assert 'email' in account_info and account_info.get('email') == 'pytest@pytest'
    assert 'time_created' in account_info
    assert 'time_updated' in account_info


def test_add_credit_balance():
    response = client.post('/add_credit_balance',
                           headers={'Authorization': f'Bearer {test_get_token("admin", "admin")}'},
                           json={'credit_amount': 50, 'user_id': 3})

    assert response.status_code == 200


def test_reduce_credit_balance():
    response = client.post('/add_credit_balance',
                           headers={'Authorization': f'Bearer {test_get_token("admin", "admin")}'},
                           json={'credit_amount': -50, 'user_id': 3})

    assert response.status_code == 200


def test_get_token(username='test', password='test'):
    response = client.post('/get_token', data={'username': username, 'password': password})

    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json() and response.json().get('token_type') == 'bearer'

    return response.json().get('access_token')


def test_health_check():
    response = client.get('/health_check')

    assert response.status_code == 200
    assert response.json() == {'message': 'I am alive and kicking!'}


def test_home():
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'message': 'Welcome to Captcha Solving Service! For help, visit /info Have fun!'}


def test_info():
    response = client.get('/info')

    assert response.status_code == 200
    assert 'message' in response.json().keys()
    assert 'example_evaluate_captcha_curl' in response.json().keys()


def test_delete_user(add_user_to_delete):
    response = client.post('/delete_user?delete_user_id=4',
                           headers={'Authorization': f'Bearer {test_get_token("admin", "admin")}'})

    assert response.status_code == 200

    with db():
        deleted_user = db.session.query(ModelUser).filter(ModelUser.username == 'delete').first()

        assert not deleted_user
