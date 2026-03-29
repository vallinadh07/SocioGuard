import requests


def get_instagram_data(profile_url):
    url = "https://instagram-statistics-api.p.rapidapi.com/profile"

    querystring = {
        "url": profile_url
    }

    headers = {
        "X-RapidAPI-Key": "07a2f6c55bmshd9c5446287efe25p1ab413jsnb5559cdd8141",
        "X-RapidAPI-Host": "instagram-statistics-api.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        print("API RESPONSE:", data)

        user = data.get("data", {})

        return {
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "posts": user.get("posts", 0)
        }

    except Exception as e:
        print("API Error:", e)
        return None