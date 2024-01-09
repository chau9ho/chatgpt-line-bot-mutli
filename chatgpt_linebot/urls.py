import sys
import os
import time
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api
from .stablediffusion import StableDiffusion
from fastapi import APIRouter, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from chatgpt_linebot.modules.music import generate_music
from chatgpt_linebot.modules.googlesheet import read_google_sheet
from chatgpt_linebot.modules.gpt import chat_completion
import config
from chatgpt_linebot.modules.matching import summarize_query_with_gpt, find_best_match_with_gpt, fetch_answer
from chatgpt_linebot.modules.gpt import chat_completion
from chatgpt_linebot.modules.faceswap import perform_face_swap  # Import the face swap function


# Google Sheets details
SHEET_ID = '1kKZKjWIwVAEUACADHyPxbjt9DTzqpynjXzbHZCB7zVw'
RANGE_NAME = 'Sheet1!A1:C17'
CREDENTIALS_PATH = '.credentials/linegptbot-410413-3b8d71621966.json'

from chatgpt_linebot.memory import Memory
from chatgpt_linebot.modules import Horoscope
from chatgpt_linebot.prompts import CEO

sys.path.append(".")
stable_diffusion = StableDiffusion()
import config

line_app = APIRouter()
memory = Memory(3)
horoscope = Horoscope()

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

@line_app.post("/callback")
async def callback(request: Request) -> str:
    signature = request.headers["X-Line-Signature"]
    body = await request.body()

    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameter")
      
    return "OK"
def save_keyword(keyword):
  with open("keyword.txt", "w") as file:
      file.write(keyword)

def get_keyword():
  try:
      with open("keyword.txt", "r") as file:
          return file.read().strip()
  except FileNotFoundError:
      return None
def save_image(message, save_path):
  response = requests.get(line_bot_api.get_message_content(message.id))
  with open(save_path, "wb") as f:
      f.write(response.content)
    
def get_target_image(keyword):
  target_image_mapping = {
    '9sum': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791778/uohug5ibcdj9u1gnmdrd.jpg',
    'sum9': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791778/uohug5ibcdj9u1gnmdrd.jpg',
    '琛': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791778/uohug5ibcdj9u1gnmdrd.jpg',
    '湛學琛': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791778/uohug5ibcdj9u1gnmdrd.jpg',
    '巢兆豪': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791789/xia3y3emzprv80ypucfy.jpg',
    '巢人': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791789/xia3y3emzprv80ypucfy.jpg',
    'chau9': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791789/xia3y3emzprv80ypucfy.jpg',
    'chau9ho': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791789/xia3y3emzprv80ypucfy.jpg',
    '鐘永祥': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791916/tli1lu72pv14teexkuh0.jpg',
    '鐘祥': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791916/tli1lu72pv14teexkuh0.jpg',
    'chung9': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791916/tli1lu72pv14teexkuh0.jpg',
    'Leo Chung': 'https://res.cloudinary.com/dr0zxmx2d/image/upload/v1704791916/tli1lu72pv14teexkuh0.jpg'
  }
  return target_image_mapping.get(keyword, None)
  
def upload_image_to_cloud_storage(image_path: str) -> str:
  

  # Retrieve Cloudinary API credentials from environment variables
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
  api_key = os.environ.get("CLOUDINARY_API_KEY")
  api_secret = os.environ.get("CLOUDINARY_API_SECRET")

  if not cloud_name or not api_key or not api_secret:
      raise ValueError("Cloudinary API credentials are missing.")

  # Configure Cloudinary with the retrieved credentials
  cloudinary.config( 
      cloud_name=cloud_name,
      api_key=api_key,
      api_secret=api_secret
  )

  # Upload the image to Cloudinary
  upload_result = cloudinary.uploader.upload(image_path)

  # Retrieve the secure URL of the uploaded image
  image_url = upload_result['secure_url']

  return image_url
@handler.add(MessageEvent, message=(ImageMessage,  TextMessage))


def handle_message(event) -> None:
    reply_token = event.reply_token
    user_message = ''  # Initialize the variable with an empty string
    if isinstance(event.message, ImageMessage):
      keyword = get_keyword()
      if keyword:
          target_image_url = get_target_image(keyword)

          source_image_path = os.path.join("img", f"target_{int(time.time())}.jpg")
          save_image(event.message, source_image_path)

          # Upload target image to cloud storage (e.g., Cloudinary)
          source_image_url = upload_image_to_cloud_storage(source_image_path)

          face_swapped_image_url = perform_face_swap(source_image_url, target_image_url)
        # Send the face-swapped image as an image message
          image_message = ImageSendMessage(original_content_url=face_swapped_image_url, preview_image_url=face_swapped_image_url)
          line_bot_api.reply_message(reply_token, messages=image_message)

          os.remove(source_image_url)

          keyword = None
          return

    if isinstance(event.message, TextMessage):
      user_message = event.message.text
      if 'faceswap_' in user_message.lower():
          keyword = user_message.lower().split('faceswap_')[1]

          # Your original face_swap_keywords mapping
          face_swap_keywords = {
              '9sum': '湛學琛',
              'sum9': '湛學琛',
              '琛': '湛學琛',
              '湛學琛': '湛學琛',
              '巢兆豪': '巢兆豪',
              '巢人': '巢兆豪',
              'chau9': '巢兆豪',
              'chau9ho': '巢兆豪',
              '鐘永祥': '鐘永祥',
              '鐘祥': '鐘永祥',
              'chung9': '鐘永祥',
              'Leo Chung': '鐘永祥'
          }

          if keyword in face_swap_keywords:
              prompt_name = face_swap_keywords[keyword]
              line_bot_api.reply_message(reply_token, TextSendMessage(text=f"Please upload a target image of {prompt_name}"))
              # Save the keyword for later use
              save_keyword(keyword)
              return

    


    if '@chat' in user_message:
        user_message = user_message.replace('@chat', '').strip()  # Extract the actual question
    
    if user_message.lower().startswith("generate image:"):
        prompt = user_message[15:].strip()
        stable_diffusion.add_prompt(prompt)
        try:
            image_url = stable_diffusion.get_url()
            image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
            line_bot_api.reply_message(reply_token, messages=image_message)
        except Exception as e:
            error_message = f"Failed to generate image. {str(e)}"
            line_bot_api.reply_message(reply_token, messages=TextSendMessage(text=error_message))

    elif user_message.startswith("music generate:"):
        music_prompt = user_message.split("music generate:", 1)[1].strip()
        if music_prompt:
            try:
                music_url = generate_music(music_prompt)
                if music_url:
                    music_message = AudioSendMessage(original_content_url=music_url, duration=12000)
                    line_bot_api.reply_message(reply_token, messages=music_message)
                else:
                    error_message = "Failed to generate music. No URL received."
                    line_bot_api.reply_message(reply_token, messages=TextSendMessage(text=error_message))
            except Exception as e:
                error_message = f"Error generating music: {str(e)}"
                line_bot_api.reply_message(reply_token, messages=TextSendMessage(text=error_message))
        else:
            error_message = "Please provide a music prompt."
            line_bot_api.reply_message(reply_token, messages=TextSendMessage(text=error_message))

    else:
        sheet_data = read_google_sheet(SHEET_ID, RANGE_NAME, CREDENTIALS_PATH)
        relevant_info = find_relevant_info(user_message, sheet_data)
        
        if relevant_info:
    # Instruct GPT to craft a natural response using the information
            prompt = f"User asked: '{user_message}'. Craft a natural and human-like response using the information: '{relevant_info}'"
            gpt_response = chat_completion([{"role": "system", "content": prompt}])
            line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=gpt_response))
        else:
    # Let GPT respond directly to the user's question
            prompt = user_message
            gpt_response = chat_completion([{"role": "user", "content": prompt}])
            line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=gpt_response))
def save_image(image_message, image_path):
  image_content = line_bot_api.get_message_content(image_message.id)
  with open(image_path, "wb") as f:
      for chunk in image_content.iter_content():
          f.write(chunk)
def find_relevant_info(user_message, sheet_data):
  user_message_lower = user_message.lower()
  for row in sheet_data[1:]:  # Skip the header row
      question, answer, keywords = row
      keywords_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
      print(f"Row: {question}, Keywords: {keywords_list}")  # Debugging print

      # Check if any keyword is a part of the user's message
      if any(keyword in user_message_lower for keyword in keywords_list):
          print(f"Match found! Answer: {answer}")  # Debugging print
          return answer

  print("No relevant keyword found.")  # Debugging print
  return None


  print("No relevant keyword found.")  # Debugging print
  return None


  print("No relevant keyword found.")  # Debugging print
  return None



@line_app.get("/recommend")
def recommend_from_yt() -> None:
    videos = recommend_videos()
    if videos:
        line_bot_api.broadcast(TextSendMessage(text=videos))
        known_group_ids = ['C6d-...', 'Ccc-...', 'Cbb-...']
        for group_id in known_group_ids:
            line_bot_api.push_message(group_id, TextSendMessage(text=videos))
        print('Successfully recommended videos')
    else:
        print('Failed to recommend videos')
    return {"status": "success" if videos else "failed", "message": "recommended videos." if videos else "no get recommended videos."}
