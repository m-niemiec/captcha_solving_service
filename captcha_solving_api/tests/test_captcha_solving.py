from pathlib import Path

import pytest

from .test_main import test_get_token, client


def test_upload_wrong_captcha():
    test_upload_file = Path('tests/images_to_test/test_0.jpeg')

    response = client.post('/upload_captcha',
                           headers={'Authorization': f'Bearer {test_get_token("pytest", "pytest")}'},
                           files={"captcha_image": test_upload_file.open('rb')})

    assert response.status_code == 400
    assert response.json().get('detail')

    detail = response.json().get('detail')

    assert 'Oops! It seems that the image you passed is not our supported captcha type' in detail


@pytest.mark.parametrize('captcha_path, captcha_solution',
                         [
                            ('tests/images_to_test/test_1.jpeg', '2KXQE'),
                            ('tests/images_to_test/test_2.jpeg', 'Z4WS3'),
                            ('tests/images_to_test/test_3.jpeg', '3AFKM'),
                            ('tests/images_to_test/test_4.jpeg', '22+8=?'),
                            ('tests/images_to_test/test_5.jpeg', '82+5=?'),
                            ('tests/images_to_test/test_6.jpeg', '73+3=?')
                         ]
                         )
def test_upload_captcha(captcha_path, captcha_solution):
    test_upload_file = Path(captcha_path)

    response = client.post('/upload_captcha',
                           headers={'Authorization': f'Bearer {test_get_token("pytest", "pytest")}'},
                           files={"captcha_image": test_upload_file.open('rb')})

    assert response.status_code == 200
    assert captcha_solution in response.json()


def test_blocked_upload_captcha():
    test_upload_file = Path('tests/images_to_test/test_1.jpeg')

    response = client.post('/upload_captcha',
                           headers={'Authorization': f'Bearer {test_get_token("pytest", "pytest")}'},
                           files={"captcha_image": test_upload_file.open('rb')})

    assert response.status_code == 400
    assert response.json().get('detail')

    detail = response.json().get('detail')

    assert detail == 'Oops! You don\'t have any credits left!'
