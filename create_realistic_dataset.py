import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 10000

# Create realistic patterns (not perfect)
data = []

for _ in range(n_samples):
    # Decide if fake or real (50/50)
    is_fake = np.random.choice([0, 1], p=[0.5, 0.5])
    
    # Features based on fake/real with overlap (not perfect separation)
    if is_fake == 1:
        # Fake account patterns (with some randomness)
        followers = np.random.randint(0, 500)
        following = np.random.randint(200, 5000)
        posts = np.random.randint(0, 50)
        account_age = np.random.randint(1, 60)
        bio_length = np.random.choice([0, np.random.randint(0, 50)], p=[0.4, 0.6])
        profile_pic = np.random.choice([0, 1], p=[0.6, 0.4])
        verified = 0
        external_links = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.3, 0.2, 0.2, 0.1, 0.1, 0.1])
        activity_rate = np.random.uniform(0.1, 2.0)
    else:
        # Real account patterns (with some randomness)
        followers = np.random.randint(500, 100000)
        following = np.random.randint(50, 2000)
        posts = np.random.randint(50, 5000)
        account_age = np.random.randint(180, 2000)
        bio_length = np.random.randint(30, 150)
        profile_pic = np.random.choice([0, 1], p=[0.05, 0.95])
        verified = np.random.choice([0, 1], p=[0.9, 0.1])
        external_links = np.random.choice([0, 1, 2, 3], p=[0.5, 0.3, 0.15, 0.05])
        activity_rate = np.random.uniform(0.5, 10.0)
    
    platform = np.random.choice(['instagram', 'twitter', 'facebook', 'linkedin', 'tiktok'])
    
    data.append({
        'platform': platform,
        'followers': followers,
        'following': following,
        'posts': posts,
        'account_age_days': account_age,
        'bio_length': bio_length,
        'profile_pic': profile_pic,
        'verified': verified,
        'external_links': external_links,
        'activity_rate': round(activity_rate, 2),
        'is_fake': is_fake
    })

df = pd.DataFrame(data)
df.to_csv('datasets/raw/social_media_fake_accounts_realistic.csv', index=False)

print(f"✅ Created realistic dataset with {len(df)} records")
print(f"\nFake accounts: {(df['is_fake']==1).sum()}")
print(f"Real accounts: {(df['is_fake']==0).sum()}")
print(f"\nSample:")
print(df.head(10))