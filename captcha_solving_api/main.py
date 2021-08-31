import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import File, UploadFile, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi_sqlalchemy import DBSessionMiddleware, db
from logzero import logger

import add_preview_users
from evaluate_request import EvaluateRequest
from manage_authorizations import Token, ManageAuthorization
from models import User as ModelUser
from models import CreditsTransaction as ModelCreditsTransaction
from recognize_captcha_type import RecognizeCaptchaType
from schema import User as SchemaUser
from schema import CreditsTransaction as SchemaCreditsTransaction
from solve_captcha import SolveCaptcha

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

load_dotenv('.env')

app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])

with db():
    add_preview_users.add_preview_users()


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


@app.post('/get_account_info')
async def login_for_account_info(token: str = Depends(oauth2_scheme)):
    user_id = await ManageAuthorization().check_token_credentials(token)
    user = db.session.query(ModelUser).filter(ModelUser.id == user_id).first()

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    account_info = {
        'id': user.id,
        'creadit_balance': user.credit_balance,
        'username': user.username,
        'email': user.email,
        'time_created': user.time_created,
        'time_updated': user.time_updated
    }

    return {'account_info': account_info}


@app.post('/upload_captcha')
async def upload_captcha(captcha_image: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    user_id = await ManageAuthorization().check_token_credentials(token)

    user = db.session.query(ModelUser).filter(ModelUser.id == user_id).first()

    if user.credit_balance < 1:
        raise HTTPException(status_code=400, detail='Oops! You don\'t have any credits left!')

    image_format, image_path, image_metadata = await EvaluateRequest().analyze_image(captcha_image)
    captcha_type = await RecognizeCaptchaType().get_captcha_type(image_path)

    solution = await SolveCaptcha().get_solution(user_id, image_format, image_path, captcha_type, image_metadata)

    return solution


@app.post('/add_user', response_model=SchemaUser)
async def add_user(user: SchemaUser):
    username_exist = db.session.query(ModelUser).filter(ModelUser.username == user.username).first()
    email_exist = db.session.query(ModelUser).filter(ModelUser.username == user.email).first()

    if username_exist or email_exist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='This username and/or email is already taken!',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    hashed_password = ManageAuthorization().get_password_hash(user.password)

    user_db = ModelUser(username=user.username,
                        email=user.email,
                        credit_balance=10,
                        password=hashed_password)
    db.session.add(user_db)
    db.session.commit()

    return user_db


@app.post('/add_credit_balance', response_model=SchemaCreditsTransaction)
async def add_credit_balance(credits_transaction: SchemaCreditsTransaction, token: str = Depends(oauth2_scheme)):
    request_user_id = await ManageAuthorization().check_token_credentials(token)

    if request_user_id != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You don\'t have admin permissions!',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user = db.session.query(ModelUser).filter(ModelUser.id == credits_transaction.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User with this ID does not exist!',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    credits_transaction_db = ModelCreditsTransaction(credit_amount=credits_transaction.credit_amount,
                                                     user_id=credits_transaction.user_id)
    db.session.add(credits_transaction_db)

    db.session.query(ModelUser).filter(ModelUser.id == credits_transaction.user_id) \
        .update({ModelUser.credit_balance: ModelUser.credit_balance + credits_transaction.credit_amount})

    db.session.commit()

    return credits_transaction_db


@app.post('/delete_user')
async def delete_user(delete_user_id, token: str = Depends(oauth2_scheme)):
    request_user_id = await ManageAuthorization().check_token_credentials(token)

    if request_user_id != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You don\'t have admin permissions!',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user = db.session.query(ModelUser).filter(ModelUser.id == delete_user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User with this ID does not exist!',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    db.session.delete(user)
    db.session.commit()

    return {'message': f'User ID - {delete_user_id} was successfully deleted!'}


@app.get('/health_check')
async def health_check():
    return {'message': 'I am alive and kicking!'}


@app.on_event('shutdown')
def shutdown_event():
    return logger.warning('Farewell! I am shutting down now ...')
