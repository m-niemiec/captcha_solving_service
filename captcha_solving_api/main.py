from datetime import timedelta

from fastapi import File, UploadFile, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from logzero import logger

from evaluate_request import EvaluateRequest
from manage_authorizations import Token, ManageAuthorization
from recognize_captcha_type import RecognizeCaptchaType
from solve_captcha import SolveCaptcha

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@app.post('/get_token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = ManageAuthorization().authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token_expires = timedelta(minutes=ManageAuthorization.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = ManageAuthorization().create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post('/upload_captcha')
async def upload_captcha(captcha_image: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    await ManageAuthorization().check_token_credentials(token)

    image_format, image_path = await EvaluateRequest().analyze_image(captcha_image)
    captcha_type = await RecognizeCaptchaType().get_captcha_type(image_path)

    solution = await SolveCaptcha().get_solution(image_format, image_path, captcha_type)

    return solution


@app.get('/health_check')
async def health_check():
    return {'message': 'I am alive and kicking!'}


@app.on_event('shutdown')
def shutdown_event():
    return logger.warning('Farewell! I am shutting down now ...')
