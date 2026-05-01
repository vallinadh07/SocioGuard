import pandas as pd
import numpy as np

df = pd.read_csv('datasets/raw/social_media_fake_accounts_realistic.csv')

np.random.seed(42)

# Add 10% mislabeled data (real-world imperfection)
mislabel_mask = np.random.random(len(df)) < 0.10
df.loc[mislabel_mask, 'is_fake'] = 1 - df.loc[mislabel_mask, 'is_fake']

# Add noise to numerical features
noise_cols = ['followers', 'following', 'posts', 'account_age_days', 'bio_length']
for col in noise_cols:
    noise = np.random.normal(0, df[col].std() * 0.15, len(df))
    df[col] = (df[col] + noise).abs().round(0)

# Save
df.to_csv('datasets/raw/social_media_fake_accounts_realistic_noisy.csv', index=False)
print("✅ Created realistic noisy dataset")
print(f"Fake accounts: {(df['is_fake']==1).sum()}")
print(f"Real accounts: {(df['is_fake']==0).sum()}")