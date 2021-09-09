import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from models import Base

client = TestClient(app)
engine = create_engine(os.environ['DATABASE_URL'], connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def test_add_user(add_user_response):
    assert add_user_response.status_code == 200
    assert 'username' in add_user_response.json() and add_user_response.json().get('username') == 'pytest'
    assert 'email' in add_user_response.json() and add_user_response.json().get('email') == 'pytest@pytest'
    assert 'password' in add_user_response.json() and add_user_response.json().get('password') != 'pytest' and \
           len(add_user_response.json().get('password')) == 60


def test_get_account_info(add_user_response, add_credit_balance, reduce_credit_balance):
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
