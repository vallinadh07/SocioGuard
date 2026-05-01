import pandas as pd
import joblib
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

print("🔍 VERIFYING YOUR MODEL...\n")

# Load data
df = pd.read_csv('datasets/raw/social_media_fake_accounts.csv')
print(f"✅ Loaded {len(df)} records")

# Encode platform
le = LabelEncoder()
df['platform_encoded'] = le.fit_transform(df['platform'])

# Features
features = ['followers', 'following', 'posts', 'account_age_days', 
            'bio_length', 'profile_pic', 'verified', 'external_links', 
            'activity_rate', 'platform_encoded']

X = df[features].fillna(0)
y = df['is_fake']

# Check class distribution
print(f"\n📊 Class distribution:")
print(f"Fake accounts (1): {(y==1).sum()}")
print(f"Real accounts (0): {(y==0).sum()}")
print(f"Fake percentage: {(y==1).mean():.1%}")

# Cross-validation (more reliable than single split)
print(f"\n🔄 Running 5-fold cross-validation...")
model = RandomForestClassifier(n_estimators=150, random_state=42)
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')

print(f"\n📈 Cross-validation results:")
print(f"Accuracy per fold: {scores}")
print(f"Mean accuracy: {scores.mean():.2%}")
print(f"Standard deviation: +/- {scores.std():.2%}")

# Check for data leakage
print(f"\n🔍 Checking for issues:")
print(f"Duplicate rows: {df.duplicated().sum()}")
print(f"Missing values: {X.isnull().sum().sum()}")

# Check if any feature perfectly predicts
print(f"\n📊 Feature correlations with 'is_fake':")
correlations = X.corrwith(y).sort_values(ascending=False)
for feature, corr in correlations.head(5).items():
    print(f"  {feature}: {corr:.3f}")

print("\n✅ Verification complete!")