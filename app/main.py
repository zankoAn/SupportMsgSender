from fastapi import FastAPI
from app.telegram.schemas import UpdateSerializer


app = FastAPI(debug=True)


@app.post("/bot/webhook/")
async def webhook(update: UpdateSerializer):
    if not update:
        return {"message": "PONG"}

    elif update.message:
        ...
    elif update.callback_query:
        ...
    else:
        print(update)

    return {"message": "PONG"}