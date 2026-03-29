import reflex as rx

from analyzers.social_media_analyzer import SocialMediaAnalyzer
from analyzers.message_analyzer import MessageAnalyzer
from analyzers.url_ml_analyzer import URLMLAnalyzer
from utils.risk_engine import RiskEngine
from utils.youtube_api import get_channel_data
from utils.database import init_db, save_scan, get_history, get_stats
from utils.database import update_behavior, get_behavior, save_pattern
import plotly.graph_objects as go
from reflex.components.lucide import icon
from utils.database import get_top_patterns

init_db()


class State(rx.State):

    page: str = "social"

    platform: str = "Instagram"  # 🔥 updated default
    profile_url: str = ""

    followers: str = ""
    following: str = ""
    posts: str = ""
    age: str = ""

    subscribers: str = ""
    videos: str = ""

    social_result: str = ""

    risk_score: int = 0
    risk_level: str = ""

    message: str = ""
    link: str = ""
    msg_link_result: str = ""

    def clear_all(self):
        self.profile_url = ""
        self.platform = "Instagram"
        self.subscribers = ""
        self.videos = ""
        self.followers = ""
        self.following = ""
        self.posts = ""
        self.age = ""
        self.social_result = ""
        self.risk_score = 0
        self.risk_level = ""

    def detect_platform(self):
        url = self.profile_url.lower()

        if "instagram" in url:
            self.platform = "Instagram"
        elif "facebook" in url:
            self.platform = "Facebook"
        elif "twitter" in url or "x.com" in url:
            self.platform = "Twitter"
        elif "youtube" in url:
            self.platform = "YouTube"
        else:
            self.platform = self.platform

    def analyze_social(self):

        data = None
        
        if self.platform == "YouTube":
            try:
                url = self.profile_url.strip()
                if "@" in url:
                    username = url.split("@")[-1]
                else:
                    username = url.rstrip("/").split("/")[-1]

                data = get_channel_data(username)

                if data:
                    self.set_followers(str(data.get("subscribers", 0)))
                    self.set_posts(str(data.get("videos", 0)))
                else:
                    self.social_result = "⚠️ Unable to fetch YouTube data"
                    return
            except:
                self.social_result = "⚠️ YouTube API error"
                return

                

        # 🔥 NEW HYBRID LOGIC (ADDED)
        try:
            if self.platform == "YouTube":
                followers = int(data.get("subscribers", 0))
                posts = int(data.get("videos", 0))
                following = 0
                age = 0
            else:
                followers = int(self.followers or 0)
                following = int(self.following or 0)
                posts = int(self.posts or 0)
                age = int(self.age or 0)
        except:
            self.social_result = "⚠️ Enter valid numbers"
            return

        score_manual = 0
        reasons_manual = []

        platform = self.platform
        reasons_manual.append(f"Platform: {platform}")

        if followers < 50 and following > 500:
            score_manual += 40
            reasons_manual.append("Low followers but high following")

        if posts < 5:
            score_manual += 20
            reasons_manual.append("Very low posts")



        if platform != "YouTube" and age < 30:
            score_manual += 25
            reasons_manual.append("New account")

        if following > 0 and (followers / following) < 0.1:
            score_manual += 30
            reasons_manual.append("Poor follower-following ratio")

        if followers > 10000:
            score_manual -= 10
            reasons_manual.append("High followers (trusted)")

        if platform == "Instagram" and posts < 3:
            score_manual += 10

        if platform == "Twitter" and followers < 10:
            score_manual += 10

        if score_manual >= 70:
            risk_manual = "FAKE ACCOUNT"
        elif score_manual >= 40:
            risk_manual = "SUSPICIOUS"
        else:
            risk_manual = "REAL ACCOUNT"

        self.social_result = f"""
--- Hybrid Social Analysis ---
Risk: {risk_manual}
Score: {score_manual}

Reasons:
{chr(10).join(reasons_manual)}
"""

    def analyze_msg_link(self): 

        msg_analyzer = MessageAnalyzer()
        url_model = URLMLAnalyzer()
        risk_engine = RiskEngine()

        msg_analyzer.train("data/message_dataset.csv")
        url_model.train("data/url_dataset.csv")

        msg_result, msg_conf = msg_analyzer.predict(self.message)
        link_result, link_conf = url_model.predict(self.link)

        risk, score, _ = risk_engine.evaluate(msg_result, link_result, None)

        reasons = []
        msg_lower = self.message.lower()
        words = set(msg_lower.split())
        stopwords = ["the", "is", "and", "to", "a", "of", "in", "for", "on", "at", "with"]
        for word in words:
            clean_word = word.strip(".,!?@#$%^&*()").lower()
            if len(clean_word) > 3 and clean_word not in stopwords:
                save_pattern(clean_word)
        url_lower = self.link.lower()


        top_patterns = get_top_patterns()

        pattern_boost = 0

        for keyword, count in top_patterns:
            if keyword in msg_lower:
                boost = min(count * 2, 20)  # limit boost
                pattern_boost += boost
                reasons.append(f"Pattern detected: '{keyword}' (+{boost})")
        if pattern_boost > 0:
            score += pattern_boost

            if score >= 70:
                risk = "HIGH"



        if link_result == "phishing":
            risk = "HIGH"
            score = max(score, 85)
            reasons.append("ML detected phishing URL")

        if msg_result == "scam":
            score = max(score, 50)
            reasons.append("ML detected scam message")

        if any(w in msg_lower for w in ["win", "free", "claim", "urgent"]):
            score = max(score, 65)
            risk = "HIGH"
            reasons.append("Suspicious keywords detected")

        if any(x in url_lower for x in [".xyz", ".top", ".click"]):
            score = max(score, 70)
            risk = "HIGH"
            reasons.append("Suspicious domain")

        if any(x in url_lower for x in ["login", "verify", "bank"]):
            score = max(score, 75)
            risk = "HIGH"
            reasons.append("Sensitive URL keywords")

        if len(self.link) > 30:
            score += 5
            reasons.append("Long URL")

        if self.link.count("-") > 2:
            score += 5
            reasons.append("Multiple '-'")

        if "https" not in url_lower:
            score += 5
            reasons.append("Non-secure link")

        risky_count, safe_count = get_behavior()

        if risky_count > 5:
            score += 10
            reasons.append("User frequently interacts with risky content")

        if safe_count > risky_count:
            score -= 5
            reasons.append("User has safe behavior history")

        if risky_count > 10:
            user_profile = "HIGH RISK USER"
        elif safe_count > risky_count:
            user_profile = "SAFE USER"
        else:
            user_profile = "MODERATE USER"

        reasons.append(f"User Profile: {user_profile}")

        top_patterns = get_top_patterns()
        keywords = [k for k, c in top_patterns]
        prediction = "No strong scam pattern detected"

        if any(k in keywords for k in ["crypto", "bitcoin", "investment"]):
            prediction = "User likely target of Crypto Scams"

        elif any(k in keywords for k in ["bank", "login", "verify"]):
            prediction = "User likely target of Phishing / Banking Scams"

        elif any(k in keywords for k in ["job", "offer", "earn"]):
            prediction = "User likely target of Job Scams"

        elif any(k in keywords for k in ["lottery", "win", "reward"]):
            prediction = "User likely target of Lottery / Reward Scams"

        reasons.append(f"Prediction: {prediction}")

        if not reasons:
            reasons.append("No major threats detected")

        save_scan(self.message, self.link, risk, score)
        update_behavior(risk)

        self.msg_link_result = f"""
Message: {msg_result} ({round(msg_conf*100,2)}%)
URL: {link_result} ({round(link_conf*100,2)}%)

Risk: {risk}
Score: {score}

Reasons:
{chr(10).join(reasons)}
"""


# ---------- UI COMPONENTS ----------
def styled_input(p, h, v):
    return rx.input(
        placeholder=p,
        value=v,
        on_change=h,
        width="100%",
        height="50px",
        padding="0px 15px",
        border_radius="12px",
        bg="#0f172a",
        border="1px solid #334155",
        color="white",
    )


def primary_button(text, action):
    return rx.button(
        text,
        on_click=action,
        width="100%",
        height="45px",
        border_radius="12px",
        bg="linear-gradient(90deg,#6366f1,#06b6d4)",
        color="white",
        _hover={"opacity": 0.85, "transform": "scale(1.05)"},
        transition="0.2s"
    )


def card(content):
    return rx.box(
        content,
        bg="rgba(15,23,42,0.7)",
        backdrop_filter="blur(12px)",
        padding="25px",
        border_radius="20px",
        box_shadow="0 10px 40px rgba(0,0,0,0.4)",
        _hover={"transform": "translateY(-5px)"},
        transition="0.3s"
    )


def nav(text, icon_name, page):
    return rx.button(
        rx.hstack(icon(icon_name), rx.text(text)),
        on_click=lambda: State.set_page(page),
        border_radius="999px",
        bg="#0f172a",
        _hover={"bg": "#1e293b", "transform": "scale(1.05)"},
        transition="0.2s"
    )


# ---------- CHARTS ----------
def pie_chart(total, high, safe):
    fig = go.Figure(data=[go.Pie(labels=["High Risk", "Safe"], values=[high, safe], hole=0.4)])
    return rx.plotly(data=fig)


def bar_chart(total, high, safe):
    fig = go.Figure([go.Bar(x=["Total", "High", "Safe"], y=[total, high, safe])])
    return rx.plotly(data=fig)


# ---------- HISTORY ----------
def history_ui():
    data = get_history()

    return rx.box(
        rx.heading("📜 History", color="white"),
        rx.vstack(*[
            card(
                rx.vstack(
                    rx.text(row[1], color="white"),
                    rx.text(row[2], color="#94a3b8"),
                    rx.text(f"{row[3]} ({row[4]})", color="red")
                )
            )
            for row in data
        ])
    )


# ---------- DASHBOARD ----------
def dashboard_ui():
    total, high, safe = get_stats()
    risky_count, safe_count = get_behavior()

    if risky_count > 10:
        user_profile = "HIGH RISK USER"
    elif safe_count > risky_count:
        user_profile = "SAFE USER"
    else:
        user_profile = "MODERATE USER"

    return rx.box(
        rx.heading("📊 Dashboard", color="white"),

        rx.grid(
            card(rx.vstack(rx.text("Total"), rx.heading(str(total)))),
            card(rx.vstack(rx.text("High Risk"), rx.heading(str(high), color="red"))),
            card(rx.vstack(rx.text("Safe"), rx.heading(str(safe), color="green"))),
            columns="3"
        ),

        rx.box(
            rx.text("User Behavior", color="gray"),
            rx.text(f"Risky Actions: {risky_count}", color="red"),
            rx.text(f"Safe Actions: {safe_count}", color="green"),
        ),

        rx.box(
            rx.text("User Risk Profile", color="gray"),
            rx.heading(user_profile, color="yellow"),
        ),

        rx.hstack(
            pie_chart(total, high, safe),
            bar_chart(total, high, safe)
        )
    )


# ---------- PAGES ----------
def social_ui():
    return rx.center(
        card(
            rx.vstack(
                rx.hstack(icon("globe"), rx.heading("Social Analyzer", color="white")),

                # 🔥 DROPDOWN
                rx.select(
                    ["Instagram", "Facebook", "Twitter", "YouTube"],
                    value=State.platform,
                    on_change=State.set_platform,
                    width="100%",
                ),

                styled_input("Profile URL (optional)", lambda v: [State.set_profile_url(v), State.detect_platform()], State.profile_url),

                # 🔥 MANUAL INPUTS
                styled_input("Followers", State.set_followers, State.followers),
                styled_input("Following", State.set_following, State.following),
                styled_input("Posts", State.set_posts, State.posts),
                styled_input("Account Age (days)", State.set_age, State.age),

                primary_button("Analyze", State.analyze_social),

                rx.text(State.social_result, color="#cbd5f5")
            )
        )
    )


def msg_ui():
    return rx.center(
        card(
            rx.vstack(
                rx.hstack(icon("message_circle"), rx.heading("Message Analyzer", color="white")),
                styled_input("Message", State.set_message, State.message),
                styled_input("Link", State.set_link, State.link),
                primary_button("Analyze", State.analyze_msg_link),
                rx.text(State.msg_link_result, color="#cbd5f5")
            )
        )
    )


# ---------- MAIN ----------
def index():
    return rx.center(
        rx.vstack(

            rx.heading(
                "🛡 SocioGuard AI",
                bg="linear-gradient(90deg,#6366f1,#06b6d4)",
                style={"WebkitBackgroundClip": "text", "color": "transparent"}
            ),

            rx.hstack(
                nav("Social", "globe", "social"),
                nav("Message", "message_circle", "msg"),
                nav("History", "clock", "history"),
                nav("Dashboard", "bar_chart", "dashboard"),
            ),

            rx.cond(
                State.page == "social",
                social_ui(),
                rx.cond(
                    State.page == "msg",
                    msg_ui(),
                    rx.cond(
                        State.page == "history",
                        history_ui(),
                        dashboard_ui()
                    )
                )
            )
        ),
        background="linear-gradient(135deg,#020617,#0f172a)",
        min_height="100vh",
        padding="40px"
    )


app = rx.App()
app.add_page(index)