import os
import uvicorn
from fastapi import FastAPI, Request
from pyngrok import ngrok
from pydantic import BaseModel
from chatgpt_linebot.urls import line_app, line_bot_api
from chatgpt_linebot.modules.stablediffusion import StableDiffusion
from linebot.models import ImageSendMessage

app = FastAPI()
app.include_router(line_app)

class LineMessage(BaseModel):
    message: str

# Initialize StableDiffusion instance
stable_diffusion = StableDiffusion()

@app.post("/linebot/message")
async def handle_message(request: Request, message: LineMessage):
    payload = await request.json()
    events = payload['events']
    reply_token = events[0]['replyToken']

    if message.message.startswith("generate image:"):
        prompt = message.message.split("generate image:", 1)[1].strip()
        stable_diffusion.add_prompt(prompt)

        try:
            image_url = stable_diffusion.get_url()
            print(f"Image URL: {image_url}")
            image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
            line_bot_api.reply_message(reply_token, image_message)
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Handle other types of messages
        # TODO: Add logic to handle other types of messages
        return {"message": "Received a non-image generation request"}

# Other routes and logic...
if __name__ == "__main__":
    port = 8000
    public_url = ngrok.connect(port)
    print(f"ngrok tunnel '{public_url}' -> 'http://127.0.0.1:{port}'")
    uvicorn.run(app, host="0.0.0.0", port=port)
