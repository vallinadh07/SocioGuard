import re


class SocialMediaAnalyzer:

    def extract_username(self, url):
        return url.rstrip("/").split("/")[-1]

    def analyze(self, platform, url, followers, following, posts, age):

        username = self.extract_username(url)

        score = 0
        reasons = []

        # ML-like logic (hybrid rules)

        if followers < 100 and following > 500:
            score += 30
            reasons.append("Low followers but high following")

        if posts < 5:
            score += 20
            reasons.append("Very few posts")

        if age < 30:
            score += 20
            reasons.append("New account")

        if re.search(r"\d{3,}", username):
            score += 20
            reasons.append("Suspicious username pattern")

        if score >= 60:
            status = "Fake / Suspicious"
        elif score >= 30:
            status = "Risky"
        else:
            status = "Likely Real"

        return status, score, reasons