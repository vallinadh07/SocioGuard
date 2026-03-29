import requests

# 🔥 DIRECT API KEY (FINAL FIX)
API_KEY = "AIzaSyD715-bzkw-gJ_Ad3r9piw2tBhSEj_vkTc"


def check_url_safety(url):

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"

    body = {
        "client": {
            "clientId": "socioguard",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(endpoint, json=body)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        if response.status_code == 200:
            data = response.json()

            if "matches" in data:
                return "UNSAFE", data["matches"]
            else:
                return "SAFE", []

        return "ERROR", []

    except Exception as e:
        print("ERROR:", e)
        return "ERROR", []