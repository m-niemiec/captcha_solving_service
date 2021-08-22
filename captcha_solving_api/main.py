from fastapi import FastAPI, File, UploadFile
from logzero import logger

from solve_captcha import SolveCaptcha

app = FastAPI()


@app.post("/upload_captcha")
async def create_upload_file(captcha_image: UploadFile = File(...)):

    solution = await SolveCaptcha().get_solution(captcha_image)

    return solution


@app.get('/health_check')
async def health_check():
    return {'message': 'I am alive and kicking!'}


@app.on_event('shutdown')
def shutdown_event():
    return logger.warning('Farewell! I am shutting down now ...')
