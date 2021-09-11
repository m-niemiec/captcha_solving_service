evaluate_captcha_curl = """curl -X POST '[URL]/upload_captcha' --header 'Authorization: Bearer [YOUR_TOKEN]' -F captcha_image=@/directory/file.jpeg"""

get_token_curl = """curl -X POST '[URL]/get_token' -F username=[YOUR_USERNAME] -F password=[YOUR_PASSWORD]"""

delete_user_curl = """curl -X POST '[URL]/delete_user?delete_user_id=[ID]' --header 'Authorization: Bearer [ADMIN_TOKEN]'"""

add_credits_curl = """curl -X POST '[URL]/add_credit_balance' -H 'accept: application/json' -H 'Content-Type: application/json' --header 'Authorization: Bearer [ADMIN_TOKEN]' -d '{"user_id": [ID], "credit_amount": [CREDIT_AMOUNT]}'"""

add_user_curl = """curl -X POST '[URL]/add_user' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"username": "[YOUR_USERNAME]", "email": "[YOUR_EMAIL]", "password": "[YOUR_PASSWORD]"}'"""

get_account_info_curl = """curl -X POST '[URL]/get_account_info' --header 'Authorization: Bearer [YOUR_TOKEN]'"""

help_text_dict = {
    'message': 'Welcome to Captcha Solving Service! You can create account here, add points and solve your captcha!'
               'Below you can find example curl requests for various endpoints.',
    'example_evaluate_captcha_curl': evaluate_captcha_curl,
    'example_get_token_curl': get_token_curl,
    'example_delete_user_curl': delete_user_curl,
    'example_add_credits_curl': add_credits_curl,
    'example_add_user_curl': add_user_curl,
    'example_get_account_info_curl': get_account_info_curl
}
