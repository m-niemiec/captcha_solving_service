from pydantic import BaseModel


class CreditsTransaction(BaseModel):
    credit_amount: int
    user_id: int

    class Config:
        orm_mode = True


class CaptchaSolveQuery(BaseModel):
    captcha_metadata: str
    captcha_type: str
    captcha_solution: str
    user_id: int

    class Config:
        orm_mode = True


class User(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True
