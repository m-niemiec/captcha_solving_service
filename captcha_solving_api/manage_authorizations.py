import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi_sqlalchemy import db
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from models import User as ModelUser

load_dotenv('.env')


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class ManageAuthorization:
    SECRET_KEY = os.environ['SECRET_KEY']
    ALGORITHM = os.environ['ALGORITHM']

    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    async def check_token_credentials(self, token):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get('sub')

            if username is None:
                raise credentials_exception

            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception

        user = db.session.query(ModelUser).filter(ModelUser.username == token_data.username).first()

        if user is None:
            raise credentials_exception

        return user.id

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str):
        user = db.session.query(ModelUser).filter(ModelUser.username == username).first()

        if not user:
            return False

        if not self.pwd_context.verify(password, user.password):
            return False

        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_jwt
