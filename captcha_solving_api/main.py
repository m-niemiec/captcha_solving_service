import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import File, UploadFile, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi_sqlalchemy import DBSessionMiddleware, db
from logzero import logger

import add_preview_user
from evaluate_request import EvaluateRequest
from manage_authorizations import Token, ManageAuthorization
from models import User as ModelUser
from recognize_captcha_type import RecognizeCaptchaType
from schema import User as SchemaUser
from solve_captcha import SolveCaptcha

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

load_dotenv('.env')

app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])

with db():
    add_preview_user.add_preview_user()


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


@app.post('/add_user', response_model=SchemaUser)
async def add_user(user: SchemaUser):
    hashed_password = ManageAuthorization().get_password_hash(user.password)

    user_db = ModelUser(username=user.username,
                        email=user.email,
                        credit_balance=10,
                        password=hashed_password)
    db.session.add(user_db)
    db.session.commit()

    return user_db


@app.get('/health_check')
async def health_check():
    return {'message': 'I am alive and kicking!'}


@app.on_event('shutdown')
def shutdown_event():
    return logger.warning('Farewell! I am shutting down now ...')
