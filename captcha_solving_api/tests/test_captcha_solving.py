from pathlib import Path

from .test_main import test_get_token, client


def test_upload_wrong_captcha(add_user_response):
    test_upload_file = Path('tests/images_to_test/test_0.jpeg')

    response = client.post('/upload_captcha',
                           headers={'Authorization': f'Bearer {test_get_token("pytest", "pytest")}'},
                           files={"captcha_image": test_upload_file.open('rb')})

    assert response.status_code == 400
    assert response.json().get('detail')

    detail = response.json().get('detail')

    assert 'Oops! It seems that the image you passed is not our supported captcha type' in detail


def test_blocked_upload_captcha(add_user_response, add_credit_balance, reduce_credit_balance):
    test_upload_file = Path('tests/images_to_test/test_1.jpeg')

    response = client.post('/upload_captcha',
                           headers={'Authorization': f'Bearer {test_get_token("pytest", "pytest")}'},
                           files={"captcha_image": test_upload_file.open('rb')})

    assert response.status_code == 400
    assert response.json().get('detail')

    detail = response.json().get('detail')

    assert detail == 'Oops! You don\'t have any credits left!'


def test_upload_captcha(upload_captcha: tuple[str, str, int]):
    assert upload_captcha[0] == upload_captcha[1]
