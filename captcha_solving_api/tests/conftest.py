from pathlib import Path

import pytest

from .test_main import client, test_get_token


@pytest.fixture(scope="session")
def add_user():
    test_password = 'pytest'

    response = client.post('/add_user', json={'username': 'pytest',
                                              'email': 'pytest@pytest',
                                              'password': test_password})

    return response


@pytest.fixture(scope="function")
def add_user_to_delete():
    test_password = 'delete'

    response = client.post('/add_user', json={'username': 'delete',
                                              'email': 'delete@delete',
                                              'password': test_password})

    return response


@pytest.fixture(scope="session")
def add_credit_balance():
    response = client.post('/add_credit_balance',
                           headers={'Authorization': f'Bearer {test_get_token("admin", "admin")}'},
                           json={'credit_amount': 50, 'user_id': 3})

    return response


@pytest.fixture(scope="session")
def reduce_credit_balance():
    response = client.post('/add_credit_balance',
                           headers={'Authorization': f'Bearer {test_get_token("admin", "admin")}'},
                           json={'credit_amount': -60, 'user_id': 3})

    return response


# fixture with indirect parametrization since currently pytest is not support better solutions
@pytest.fixture(scope="session", params=[
                                        ('tests/images_to_test/test_1.jpeg', '2KXQE', 1),
                                        ('tests/images_to_test/test_2.jpeg', 'Z4WS3', 2),
                                        ('tests/images_to_test/test_3.jpeg', '3AFKM', 3),
                                        ('tests/images_to_test/test_4.jpeg', '30', 4),
                                        ('tests/images_to_test/test_5.jpeg', '87', 5),
                                        ('tests/images_to_test/test_6.jpeg', '76', 6)
                                        ])
def upload_captcha(request) -> tuple[str, str, int]:
    path = request.param[0]
    solution = request.param[1]
    task_index = request.param[2]

    test_upload_file = Path(path)

    response = client.post('/upload_captcha',
                           headers={'Authorization': f'Bearer {test_get_token("test", "test")}'},
                           files={"captcha_image": test_upload_file.open('rb')})

    return response.json(), solution, task_index
