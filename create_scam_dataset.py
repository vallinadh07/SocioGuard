import pandas as pd
import numpy as np
import re

np.random.seed(42)
n_samples = 20000

print("📊 Creating SCAM TEXT dataset...")

# Scam patterns
scam_patterns = [
    # Financial scams
    ("bank", "Your account has been suspended. Verify now!"),
    ("bank", "Unusual activity detected. Login immediately."),
    ("crypto", "Double your Bitcoin in 24 hours! Limited offer."),
    ("investment", "Guaranteed 500% returns. Invest now!"),
    ("loan", "You're approved for $50,000 loan. Click here."),
    
    # Prize scams
    ("prize", "CONGRATULATIONS! You won $1000 Amazon gift card!"),
    ("lottery", "You're the lucky winner of our lottery! Claim prize."),
    ("giveaway", "Free iPhone giveaway! Click to claim."),
    
    # Urgent scams
    ("urgent", "URGENT: Your account will be deleted!"),
    ("suspension", "Immediate action required. Account suspended."),
    
    # Phishing
    ("phishing", "Verify your password here: secure-login.com"),
    ("login", "Someone tried to login to your account. Verify now."),
    
    # Fake offers
    ("free", "FREE $500! Limited time only."),
    ("discount", "90% discount today only! Click here.")
]

# Safe patterns
safe_patterns = [
    "Hey, how are you doing today?",
    "The project meeting is at 3pm tomorrow.",
    "Thanks for your help with the presentation.",
    "Don't forget to pick up groceries on your way home.",
    "What time should we meet for lunch?",
    "I really enjoyed the movie last night.",
    "Happy Birthday! Hope you have a great day!",
    "Can you send me the document by Friday?",
    "The weather is beautiful today.",
    "Let's catch up over coffee this weekend."
]

data = []
for _ in range(n_samples):
    is_scam = np.random.choice([0, 1], p=[0.5, 0.5])
    
    if is_scam == 1:
        # Generate scam message
        category, pattern = scam_patterns[np.random.randint(len(scam_patterns))]
        text = pattern
        # Add random variations
        if np.random.random() > 0.5:
            text = text.upper()
        if np.random.random() > 0.7:
            text = text + " !!!"
    else:
        # Generate safe message
        text = np.random.choice(safe_patterns)
        # Add minor variations
        if np.random.random() > 0.8:
            text = text.lower()
    
    data.append({'text': text, 'is_scam': is_scam})

df_text = pd.DataFrame(data)
df_text.to_csv('datasets/raw/scam_text_dataset.csv', index=False)
print(f"✅ Text dataset: {len(df_text)} records")
print(f"   Scam: {(df_text['is_scam']==1).sum()}, Safe: {(df_text['is_scam']==0).sum()}")

# ========== CREATE URL DATASET ==========
print("\n📊 Creating SCAM URL dataset...")

scam_urls = [
    "http://bit.ly/3fR9xQ2",
    "https://paypal-verify.xyz/login",
    "http://secure-login.ru/verify",
    "https://amazon-gift.biz/claim",
    "http://free-reward.com/winner",
    "https://bank-secure.xyz/confirm",
    "http://192.168.1.100/login",
    "https://facebook-verify.net/secure",
    "http://tinyurl.com/2x3y4z",
    "https://instagram-verify.ru",
    "http://netflix-account.com/verify",
    "https://apple-id-secure.com",
    "http://google-security-alert.com",
    "https://paypal-security.net",
    "http://amazon-prime-verify.com"
]

safe_urls = [
    "https://www.google.com",
    "https://github.com/yourusername",
    "https://stackoverflow.com/questions",
    "https://www.linkedin.com/in/username",
    "https://www.amazon.com/dp/B08N5WRWNW",
    "https://www.netflix.com/browse",
    "https://www.paypal.com/signin",
    "https://www.microsoft.com/en-us",
    "https://www.facebook.com",
    "https://www.instagram.com",
    "https://twitter.com/home",
    "https://www.youtube.com",
    "https://www.reddit.com",
    "https://en.wikipedia.org/wiki/Main_Page",
    "https://www.apple.com"
]

url_data = []
for _ in range(n_samples):
    is_scam = np.random.choice([0, 1], p=[0.5, 0.5])
    
    if is_scam == 1:
        url = np.random.choice(scam_urls)
    else:
        url = np.random.choice(safe_urls)
    
    # Extract URL features
    url_data.append({
        'url': url,
        'url_length': len(url),
        'num_dots': url.count('.'),
        'num_slashes': url.count('/'),
        'has_https': 1 if url.startswith('https') else 0,
        'has_ip': 1 if re.search(r'\d+\.\d+\.\d+\.\d+', url) else 0,
        'has_digits': 1 if any(c.isdigit() for c in url) else 0,
        'is_shortened': 1 if any(x in url for x in ['bit.ly', 'tinyurl', 'shorturl']) else 0,
        'is_scam': is_scam
    })

df_url = pd.DataFrame(url_data)
df_url.to_csv('datasets/raw/scam_url_dataset.csv', index=False)
print(f"✅ URL dataset: {len(df_url)} records")
print(f"   Scam: {(df_url['is_scam']==1).sum()}, Safe: {(df_url['is_scam']==0).sum()}")

print("\n✅ Both datasets created successfully!")