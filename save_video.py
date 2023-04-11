import time
import requests
from numpy import asarray
from PIL import Image, ImageOps
from io import BytesIO
from moviepy.editor import CompositeVideoClip, AudioFileClip, ImageClip
import json

def save_video_from_subreddit(subreddit_name, reddit_client):
  ASPECT_RATIO = (640, 360)
  FINAL_VIDEO_LENGHT = 60 + 55
  TIME_PER_IMG = 5
  IMG_AMOUNT = FINAL_VIDEO_LENGHT / TIME_PER_IMG
  SAVE_FILE = f"./.saved.{subreddit_name}.json"
  OUTPUT_FILE = f"./{subreddit_name}.{str(time.time())[-4:-1]}.mp4"

  saved_options = {}
  try:
    with open(SAVE_FILE, "r") as f:
      saved_options = json.loads(f.read())
  except FileNotFoundError: pass
  saved_options["already_generated"] = saved_options.get("already_generated", [])

  image_urls = []
  image_clips: list[ImageClip] = []

  print(f"{subreddit_name} | Finding posts")
  for submission in reddit_client.subreddit(subreddit_name).hot(limit = IMG_AMOUNT + 20):
    if submission.over_18: continue
    if submission.id in saved_options["already_generated"]: continue

    if len(image_urls) < IMG_AMOUNT and "i.redd.it" in submission.url:
      image_urls.append(submission.url)
      saved_options["already_generated"].append(submission.id)
    elif len(image_urls) >= IMG_AMOUNT:
      break

  if len(image_urls) < IMG_AMOUNT:
    print(f"{subreddit_name} | Not enough new hot posts on subreddit. (only {len(image_urls)})")
    return False

  print(f"{subreddit_name} | Fetching images")
  for i, url in enumerate(image_urls):
    data = requests.get(url).content
    img = Image.open(BytesIO(data))
    img = ImageOps.pad(img, ASPECT_RATIO)

    formatter = {"PNG": "RGBA", "JPEG": "RGB"}
    rgbimg = Image.new(formatter.get(img.format, 'RGB'), img.size)
    rgbimg.paste(img)

    image_clips.append(ImageClip(asarray(rgbimg), duration=TIME_PER_IMG).set_start(i * TIME_PER_IMG))

  audio_clip = AudioFileClip("./background.mp3")

  video_clip: CompositeVideoClip = CompositeVideoClip(image_clips)
  video_clip = video_clip.set_audio(audio_clip)
  video_clip = video_clip.set_duration(FINAL_VIDEO_LENGHT)

  print(f"{subreddit_name} | Creating video")
  video_clip.write_videofile(OUTPUT_FILE, fps = 24)

  with open(SAVE_FILE, "w+") as f:
    f.write(json.dumps(saved_options))
    
  return True