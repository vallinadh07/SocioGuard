import re
from urllib.parse import urlparse


class LinkAnalyzer:

    def __init__(self):

        self.shorteners = [
            "bit.ly",
            "tinyurl.com",
            "goo.gl",
            "t.co",
            "ow.ly",
            "is.gd"
        ]

        self.suspicious_keywords = [
            "login",
            "verify",
            "secure",
            "account",
            "bank",
            "update",
            "free",
            "money",
            "prize"
        ]


    def analyze(self, url):

        reasons = []

        parsed = urlparse(url)
        domain = parsed.netloc

        # Check shortened URL
        if domain in self.shorteners:
            reasons.append("Shortened URL detected")

        # Check suspicious keywords
        for keyword in self.suspicious_keywords:
            if keyword in url.lower():
                reasons.append(f"Suspicious keyword detected: {keyword}")

        # Check unusual characters
        if re.search(r"[@\-_=]{2,}", url):
            reasons.append("Unusual URL structure detected")

        if reasons:
            risk = "Dangerous"
        else:
            risk = "Safe"

        return risk, reasons