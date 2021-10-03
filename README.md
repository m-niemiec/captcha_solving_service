# **Captcha Solving Service**

![captcha_solving_service_screen_main](https://user-images.githubusercontent.com/59567076/135750575-c70c8153-f85f-4511-80d0-f1844a35c6fc.jpg)

This time I decided to create something bigger, with more depth to it in order to learn more. 

My main concept was to create a product (mock-up SaaS) that would allow users to send their captcha images and receive solutions in simple text format.

In order to achieve this I had to solve several problems and divide my project into 4 parts.

Working on this project was very fun and fulfilling. I had many opportunities to work closer and explore more deeply things like creating GUI, design patterns, asynchronous programming and finally Docker and docker-compose with AWS and EC2.

## **Part I - Scraping Captcha Dataset:**

![captcha_solving_service_screen_1](https://user-images.githubusercontent.com/59567076/135750569-3061824f-38aa-432c-bd3c-5808e8f80d75.jpg)

Firstly I selected 2 example captcha types and with Scrapy I needed to gather enough data to have a learning dataset for my model.

After solving some problems with monkey patching MediaPipeline it went smoothly.

## **Part II - Captcha Renaming Tool:**

![captcha_solving_service_screen_2](https://user-images.githubusercontent.com/59567076/135750570-98c9225b-db67-44e6-932e-a125cc3f321b.jpg)

After I gathered captcha images I had to come up with a better way of renaming them than the ones that are built in operating systems because of dataset sizes.

I decided to build an application with the help of Tkinter and Pillow. The app had several tools to make renaming captcha images easier and faster. Amongst others, it helped user with faster switching between images after assigning a new name, had options to increase or decrease size and contrast or convert captcha to black and white mode.

## **Part III - Captcha Solving OCR:**

![captcha_solving_service_screen_3](https://user-images.githubusercontent.com/59567076/135750571-65e167d4-5e80-4caf-a35d-2f63b3787c05.jpg)

When all captcha images were renamed with proper solutions, it was time to actually build and save Machine Learning models with Tensorflow and Keras.

I needed three models, one to distinguish between captcha types and two for predicting proper solutions of those captcha types.

In this task, the book "Neural Network Projects with Python" written by James Loy and website keras.io with articles by A_K_Nain were really helpful.

## **Part IV - Captcha Solving API:**

![captcha_solving_service_screen_4](https://user-images.githubusercontent.com/59567076/135750573-bf700f8f-df29-4ff5-b750-21758d358d63.jpg)

The final part of the whole project. I decided to go with Fast API for this task to also explore deeper asynchronous programming and PostgreSQL with SQLAlchemy for database tasks. For security, I used oauth2. I wanted to create an API so every potential "user" could get their captcha solved. I created several endpoints for things like, solving captcha, adding, deleting, viewing info about users and adding credits.

API was accepting CURL requests formdata with captcha images, which were processed by saved ML models from previous step and returning a solution. I also decided to write tests using pytest to make my life easier.

I Dockerized the whole API alongside PostgreSQL and PgAdmin using docker-compose.

As a final touch, I decided to host it on AWS with EC2. Here is address - http://18.189.161.236/

Example captcha images to solve:

![captcha_solving_service_test_captcha_1](https://user-images.githubusercontent.com/59567076/135750576-bfaa8ebd-cbbe-4172-8498-a0d24a3a2993.jpeg)
![captcha_solving_service_test_captcha_2](https://user-images.githubusercontent.com/59567076/135750577-20099cd2-c462-41e9-b042-398240c9af24.jpeg)

### **Example API CURLs:**

_Test user:_ Username - `test` Password - `test`

_Admin user:_ Username - `admin` Password - `admin` (for deleting users and adding more credits)

_Solve Captcha:_

`curl -X POST '[URL]/upload_captcha' --header 'Authorization: Bearer [YOUR_TOKEN]' -F captcha_image=@/directory/file.jpeg"`

_Add User:_

`curl -X POST '[URL]/add_user' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{\"username\": \"[YOUR_USERNAME]\", \"email\": \"[YOUR_EMAIL]\", \"password\": \"[YOUR_PASSWORD]\"}'`

_Get Token:_

`curl -X POST '[URL]/get_token' -F username=[YOUR_USERNAME] -F password=[YOUR_PASSWORD]`

_Add Credits:_

`curl -X POST '[URL]/add_credit_balance' -H 'accept: application/json' -H 'Content-Type: application/json' --header 'Authorization: Bearer [ADMIN_TOKEN]' -d '{\"user_id\": [ID], \"credit_amount\": [CREDIT_AMOUNT]}'`

_Get Account Info:_

`curl -X POST '[URL]/get_account_info' --header 'Authorization: Bearer [YOUR_TOKEN]'`

_Delete User:_

`curl -X POST '[URL]/delete_user?delete_user_id=[ID]' --header 'Authorization: Bearer [ADMIN_TOKEN]'`

### **If you would like to build API on your machine, you need to do following steps:**

(you need to have docker and docker-compose installed on your machine)

1. Download 2 files from repo:
   1. `docker-compose-development.yml`
   2. `.env`
2. `cd` into download directory
3. run `docker-compose -f docker-compose-deployment.yml --env-file env up` command to build and start images
4. After build will finish, the API will be available on address http://127.0.0.1/ or http://0.0.0.0/

API is also available online on AWS EC2 on this address - http://18.189.161.236/

**Some of the technologies used** - Scrapy, Tkinter, Pillow, Py2app, Tensorflow, Keras, FastAPI, PostgreSQL, SQLAlchemy, pytest, Docker, docker-compose, AWS, EC2

It was really fun to work on this.

Thank You :-)