import pandas as pd
import numpy as np
import re

np.random.seed(42)
n_samples = 20000

print("📊 Creating ENHANCED SCAM URL dataset...")

scam_urls = [
    # PayPal scams
    "http://paypal-verify.xyz/login",
    "https://paypal-security.net/verify",
    "http://paypal.com.secure-login.ru",
    
    # Banking scams
    "http://bank-secure.xyz/login",
    "https://chase-verify.com",
    "http://wellsfargo-alert.net",
    
    # Amazon scams
    "http://amazon-gift.biz/claim",
    "https://amazon-verify.net/login",
    "http://amazon.com.security-check.ru",
    
    # Facebook scams
    "http://facebook-verify.xyz",
    "https://facebook-security.net/login",
    "http://fb-account-verify.com",
    
    # Generic phishing
    "http://secure-login.ru/verify",
    "https://account-verify.org/login",
    "http://login-secure.net/verify",
    "https://verify-account.xyz",
    "http://bit.ly/3fR9xQ2",
    "http://tinyurl.com/scamlink",
    "http://192.168.1.100/login",
    "https://secure-verify.ru",
]

safe_urls = [
    "https://www.google.com",
    "https://www.paypal.com",
    "https://www.amazon.com",
    "https://www.facebook.com",
    "https://www.chase.com",
    "https://www.wellsfargo.com",
    "https://github.com",
    "https://stackoverflow.com",
    "https://www.linkedin.com",
    "https://www.netflix.com",
    "https://www.microsoft.com",
    "https://www.apple.com",
]

data = []
for _ in range(n_samples):
    is_scam = np.random.choice([0, 1], p=[0.5, 0.5])
    
    if is_scam == 1:
        url = np.random.choice(scam_urls)
        # Add random variations
        if np.random.random() > 0.7:
            url = url.replace("http://", "https://")
    else:
        url = np.random.choice(safe_urls)
    
    # Extract features
    data.append({
        'url': url,
        'url_length': len(url),
        'num_dots': url.count('.'),
        'num_slashes': url.count('/'),
        'has_https': 1 if url.startswith('https') else 0,
        'has_digits': 1 if any(c.isdigit() for c in url) else 0,
        'is_scam': is_scam
    })

df = pd.DataFrame(data)
df.to_csv('datasets/raw/scam_url_dataset.csv', index=False)
print(f"✅ Created {len(df)} URL samples")
print(f"   Scam: {(df['is_scam']==1).sum()}, Safe: {(df['is_scam']==0).sum()}")
print(f"\n📋 Sample scam URLs:")
print(df[df['is_scam']==1]['url'].head(10).to_string())