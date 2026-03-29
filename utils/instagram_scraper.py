import requests


def get_instagram_data(username):
    try:
        url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            return None

        data = res.json()

        user = data["graphql"]["user"]

        return {
            "followers": user["edge_followed_by"]["count"],
            "following": user["edge_follow"]["count"],
            "posts": user["edge_owner_to_timeline_media"]["count"]
        }

    except Exception as e:
        print("Instagram Error:", e)
        return None