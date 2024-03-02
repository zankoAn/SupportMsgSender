from fastapi import FastAPI
from app.telegram.schemas import UpdateSerializer
from app.telegram.handlers import BaseHandler


app = FastAPI(debug=True)


@app.post("/bot/webhook/")
async def webhook(update: UpdateSerializer):
    try:
        if update.message:
            return BaseHandler(update).run()

        if update.callback_query:
            ...
    except Exception as error:
        print(error)
    return {"message": "PONG"}