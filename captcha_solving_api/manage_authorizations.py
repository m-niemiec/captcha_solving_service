from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


class ManageAuthorization:
    SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    fake_users_db = {
        'johndoe': {
            'username': 'johndoe',
            'full_name': 'John Doe',
            'email': 'johndoe@example.com',
            'hashed_password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
            'disabled': False,
        }
    }

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

        user = self.get_user(self.fake_users_db, username=token_data.username)

        if user is None:
            raise credentials_exception

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(self.fake_users_db, username)

        if not user:
            return False

        if not self.verify_password(password, user.hashed_password):
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

    @staticmethod
    def get_user(db, username: str):
        if username in db:
            user_dict = db[username]

            return UserInDB(**user_dict)
