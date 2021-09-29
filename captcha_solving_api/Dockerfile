FROM python:3-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /captcha_solving_api
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /captcha_solving_api
EXPOSE 8000