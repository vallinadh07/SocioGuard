import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ❗ FIX THIS LINE (VERY IMPORTANT)
API_KEY = "AIzaSyCo2gh61YzKz0Y3JLl3Ju5XTO5MwQsqP_c"


def get_channel_data(username):
    try:
        # 🔥 Clean username
        username = username.replace("@", "").strip()

        print("USERNAME:", username)  # ✅ HERE

        # 🔥 Step 1: Search channel
        search_url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&type=channel&q={username}&key={API_KEY}"
        )

        response = requests.get(search_url)
        data = response.json()

        print("SEARCH RESPONSE:", data)  # ✅ HERE

        if "items" not in data or len(data["items"]) == 0:
            return None

        channel_id = data["items"][0]["snippet"]["channelId"]

        # 🔥 Step 2: Get channel stats
        stats_url = (
            f"https://www.googleapis.com/youtube/v3/channels"
            f"?part=statistics,snippet&id={channel_id}&key={API_KEY}"
        )

        stats_response = requests.get(stats_url)
        stats_data = stats_response.json()

        print("STATS RESPONSE:", stats_data)  # ✅ HERE

        if "items" not in stats_data or len(stats_data["items"]) == 0:
            return None

        channel = stats_data["items"][0]

        return {
            "subscribers": int(channel["statistics"].get("subscriberCount", 0)),
            "videos": int(channel["statistics"].get("videoCount", 0)),
            "title": channel["snippet"].get("title", "Unknown")
        }

    except Exception as e:
        print("❌ YouTube API Error:", e)
        return None