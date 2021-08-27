from fastapi import FastAPI, File, UploadFile, Form
from logzero import logger

from evaluate_request import EvaluateRequest
from recognize_captcha_type import RecognizeCaptchaType
from solve_captcha import SolveCaptcha

app = FastAPI()


@app.post("/upload_captcha")
async def create_upload_file(captcha_image: UploadFile = File(...), api_key: str = Form(...)):
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
