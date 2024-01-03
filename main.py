import os
import uvicorn
import replicate
from fastapi import FastAPI
from pyngrok import ngrok
from pydantic import BaseModel
from chatgpt_linebot.urls import line_app

app = FastAPI()
app.include_router(line_app)

class StableDiffusion:
    def __init__(self):
        self.prompt = "a vision of paradise. unreal engine"

    def get_url(self):
        model = replicate.models.get("stability-ai/stable-diffusion")
        version = model.versions.get("db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf")

        inputs = {
            'prompt': self.prompt,
            'image_dimensions': "768x768",
            'num_outputs': 1,
            'num_inference_steps': 50,
            'guidance_scale': 7.5,
            'scheduler': "DPMSolverMultistep",
        }

        output = version.predict(**inputs)
        output = str(output).replace("\'", "").replace("[", "").replace("]", "")
        return output

    def add_prompt(self, text):
        self.prompt = text

class LineMessage(BaseModel):
    message: str

# Initialize StableDiffusion instance
stable_diffusion = StableDiffusion()

@app.post("/linebot/message")
async def handle_message(message: LineMessage):
    if message.message.startswith("generate image:"):
        prompt = message.message.split("generate image:", 1)[1].strip()
        stable_diffusion.add_prompt(prompt)

        try:
            image_url = stable_diffusion.get_url()
            # Logic to send the image URL back to the user via LINE Messaging API
            # Example: line_bot_api.reply_message(reply_token, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
        except Exception as e:
            # Handle exceptions and inform the user
            # Example: line_bot_api.reply_message(reply_token, TextSendMessage(text="Failed to generate image."))
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
