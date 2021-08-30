FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /captcha_solving_api
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /captcha_solving_api
EXPOSE 8000