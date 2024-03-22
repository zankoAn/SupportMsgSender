## Overview
This project is a straightforward Telegram bot developed using FastAPI, SQLAlchemy, and Pydantic.
It serves as a support ticket submission system, allowing admin users to submit support tickets to Telegram by providing proxies, email/phone and messages. 
The project focuses on a clean structure that integrates FastAPI for handling incoming Telegram webhook updates, while Pydantic is used for serialization.

<br>


## Prerequisites
- Python 3.10 or newer (for manual installation).
<br>

## Installation
To set up the project, choose your preferred installation method:

### 1.Manual
1. Clone the repository.
2. Navigate to the project directory: `cd SupportMsgSender`
3. Create the `.env.ini` file and add the environment variables(using `.env.example` as a template).
4. Install dependencies: `pip install -r requirements.txt`.
5. Migrate the migration files: `python manage.py migrate`.
6. Load default fixtures: `python manage.py loadmsg`.
7. Run the application: `python manage.py runserver`.

### 2.Docker
1. Install Docker.
2. Clone the repository.
3. Navigate to the project directory: `cd SupportMsgSender`
4. Create the `.env.ini` file and add the environment variables(using `.env.example` as a template).
5. Run the application using Docker: `docker compose up`.

<br>

## Setting up Telegram Webhook
To enable the Telegram webhook, follow these additional steps:
1. Open the `.env.example` file and locate the `WEBHOOK_URL` field.
2. Edit the `WEBHOOK_URL`. Replace `YOUR_TOKEN` and `YOUR_DOMAIN` with your bot token and domain, respectively.
3. Copy the updated URL and paste it into your browser to set up the Telegram webhook.

<br>


## Running Help
To view available command-line options and help, run the following command:

### manual
```bash
python manage.py -h
```
### Docker
```bash
 docker exec tm-app python manage.py -h
```
<br>


## Promoting a User to Admin
To enable the bot to respond to users, it's necessary to promote a user to an admin role. You can promote a user to admin with:


### Manual:
```bash
python manage.py promote user_id admin
```

### Docker:
```bash
 docker exec tm-app python manage.py promote user_id admin
```


