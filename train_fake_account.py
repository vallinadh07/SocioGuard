import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

os.makedirs('backend/models', exist_ok=True)

print("📂 Loading your dataset...")

# Load dataset
df = pd.read_csv('datasets/raw/social_media_fake_accounts.csv')
print(f"✅ Loaded {len(df)} records")
print(f"\n📊 Columns: {df.columns.tolist()}")

# Encode platform (convert text to numbers)
le = LabelEncoder()
df['platform_encoded'] = le.fit_transform(df['platform'])

# ALL useful features (except 'is_fake' and original 'platform')
features = ['followers', 'following', 'posts', 'account_age_days', 
            'bio_length', 'profile_pic', 'verified', 'external_links', 
            'activity_rate', 'platform_encoded']

print(f"\n🔍 Using {len(features)} features: {features}")

X = df[features]
y = df['is_fake']

# Handle any missing values
X = X.fillna(0)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n🤖 Training Random Forest model...")
model = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=12)
model.fit(X_train, y_train)

# Evaluate
accuracy = model.score(X_test, y_test)
print(f"✅ Model accuracy: {accuracy:.2%}")

# Feature importance
print("\n📈 Feature importance:")
importance_df = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(importance_df.to_string(index=False))

# Save model, features, and label encoder
joblib.dump(model, 'backend/models/fake_account_model.pkl')
joblib.dump(features, 'backend/models/fake_account_features.pkl')
joblib.dump(le, 'backend/models/platform_encoder.pkl')
print("\n💾 Saved: model, features, and platform encoder")