import sys
import praw
import threading
import os
from dotenv import load_dotenv
from save_video import save_video_from_subreddit
load_dotenv()

if len(sys.argv) < 2:
  print("""Missing arguments.
Usage: python main.py [...subreddits]""")
  exit(1)

subreddits = sys.argv[1:]

print("Logging in to reddit...", end = " ")
reddit = praw.Reddit(
  client_secret = os.environ["CLIENT_SECRET"],
  client_id = os.environ["CLIENT_ID"],
  user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 RuxitSynthetic/1.0 v5359377870492043950 t8052286838287810618"
)
print("Done!")

for subreddit in subreddits:
  t = threading.Thread(
    target = save_video_from_subreddit,
    args = [ subreddit, reddit ]
  )
  t.start()