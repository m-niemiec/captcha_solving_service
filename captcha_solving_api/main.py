from fastapi import FastAPI
from logzero import logger

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/health_check')
async def health_check():
    return {'message': 'I am alive and kicking!'}


@app.on_event('shutdown')
def shutdown_event():
    return logger.warning('Farewell! I am shutting down now ...')
