import os
import uvicorn
from fastapi import FastAPI
from pyngrok import ngrok
from chatgpt_linebot.urls import line_app

app = FastAPI()
app.include_router(line_app)

if __name__ == "__main__":
    port = 8000
    public_url = ngrok.connect(port)
    print(f"ngrok tunnel '{public_url}' -> 'http://127.0.0.1:{port}'")
    uvicorn.run(app, host="0.0.0.0", port=port)
