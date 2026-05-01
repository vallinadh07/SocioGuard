import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs('backend/models', exist_ok=True)

print("="*60)
print("🔬 SOCIO GUARD - ADVANCED ML MODEL TRAINING")
print("="*60)

# Load your dataset
df = pd.read_csv('datasets/raw/social_media_fake_accounts_realistic.csv')
print(f"\n📊 Loaded {len(df)} records")
print(f"📊 Columns: {df.columns.tolist()}")

# Encode platform
le = LabelEncoder()
df['platform_encoded'] = le.fit_transform(df['platform'])

# Features that exist in your dataset (based on actual columns)
features = [
    'followers',
    'following', 
    'posts',
    'account_age_days',
    'bio_length',
    'profile_pic',
    'verified',
    'external_links',
    'activity_rate',
    'platform_encoded'
]

# Derived features (from research paper recommendations)
df['followers_following_ratio'] = df['followers'] / (df['following'] + 1)
df['engagement_potential'] = (df['followers'] + df['posts']) / (df['account_age_days'] + 1)
df['completeness_score'] = df['profile_pic']  # Since has_bio doesn't exist, just use profile_pic

# Add new derived features
features.extend(['followers_following_ratio', 'engagement_potential', 'completeness_score'])

print(f"\n🔍 Using {len(features)} features: {features}")

X = df[features].fillna(0)
y = df['is_fake']

print(f"\n📊 Class distribution:")
print(f"   Fake accounts (1): {(y==1).sum()}")
print(f"   Real accounts (0): {(y==0).sum()}")
print(f"   Fake percentage: {(y==1).mean():.1%}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\n📈 Training set: {len(X_train)} records")
print(f"📈 Test set: {len(X_test)} records")

# ========== MULTIPLE ML ALGORITHMS ==========
print("\n" + "="*60)
print("🤖 TRAINING MULTIPLE ML ALGORITHMS")
print("="*60)

results = {}
models = {}

# 1. Random Forest
print("\n🌲 1. Random Forest Classifier")
rf = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)
rf.fit(X_train_scaled, y_train)
y_pred_rf = rf.predict(X_test_scaled)
acc_rf = accuracy_score(y_test, y_pred_rf)
results['Random Forest'] = acc_rf
models['Random Forest'] = rf
print(f"   ✅ Accuracy: {acc_rf:.2%}")

# 2. Gradient Boosting
print("\n📈 2. Gradient Boosting Classifier")
gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
gb.fit(X_train_scaled, y_train)
y_pred_gb = gb.predict(X_test_scaled)
acc_gb = accuracy_score(y_test, y_pred_gb)
results['Gradient Boosting'] = acc_gb
models['Gradient Boosting'] = gb
print(f"   ✅ Accuracy: {acc_gb:.2%}")

# 3. Neural Network
print("\n🧠 3. Neural Network (MLP Classifier)")
nn = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
nn.fit(X_train_scaled, y_train)
y_pred_nn = nn.predict(X_test_scaled)
acc_nn = accuracy_score(y_test, y_pred_nn)
results['Neural Network'] = acc_nn
models['Neural Network'] = nn
print(f"   ✅ Accuracy: {acc_nn:.2%}")

# 4. Support Vector Machine
print("\n⚡ 4. Support Vector Machine (SVM)")
svm = SVC(kernel='rbf', probability=True, random_state=42)
svm.fit(X_train_scaled, y_train)
y_pred_svm = svm.predict(X_test_scaled)
acc_svm = accuracy_score(y_test, y_pred_svm)
results['SVM'] = acc_svm
models['SVM'] = svm
print(f"   ✅ Accuracy: {acc_svm:.2%}")

# 5. Logistic Regression
print("\n📊 5. Logistic Regression")
lr = LogisticRegression(random_state=42, max_iter=1000)
lr.fit(X_train_scaled, y_train)
y_pred_lr = lr.predict(X_test_scaled)
acc_lr = accuracy_score(y_test, y_pred_lr)
results['Logistic Regression'] = acc_lr
models['Logistic Regression'] = lr
print(f"   ✅ Accuracy: {acc_lr:.2%}")

# ========== RESULTS COMPARISON ==========
print("\n" + "="*60)
print("📊 MODEL COMPARISON RESULTS")
print("="*60)

# Sort by accuracy
sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

for i, (model_name, accuracy) in enumerate(sorted_results, 1):
    bar = "█" * int(accuracy * 50)
    print(f"{i}. {model_name:20} : {accuracy:.2%} {bar}")

best_model_name = sorted_results[0][0]
best_accuracy = sorted_results[0][1]
print(f"\n🏆 BEST MODEL: {best_model_name} with {best_accuracy:.2%} accuracy")

# ========== SAVE BEST MODEL ==========
print("\n" + "="*60)
print("💾 SAVING BEST MODEL")
print("="*60)

best_model = models[best_model_name]

# Save model, scaler, and features
joblib.dump(best_model, 'backend/models/fake_account_model.pkl')
joblib.dump(scaler, 'backend/models/fake_account_scaler.pkl')
joblib.dump(features, 'backend/models/fake_account_features.pkl')
joblib.dump(le, 'backend/models/platform_encoder.pkl')

print(f"✅ Saved {best_model_name} to backend/models/")

# ========== DETAILED REPORT FOR BEST MODEL ==========
print("\n" + "="*60)
print(f"📋 DETAILED REPORT - {best_model_name}")
print("="*60)

# Get predictions for best model
if best_model_name == 'Random Forest':
    y_pred_best = y_pred_rf
elif best_model_name == 'Gradient Boosting':
    y_pred_best = y_pred_gb
elif best_model_name == 'Neural Network':
    y_pred_best = y_pred_nn
elif best_model_name == 'SVM':
    y_pred_best = y_pred_svm
else:
    y_pred_best = y_pred_lr

# Cross-validation score
cv_scores = cross_val_score(best_model, X_train_scaled, y_train, cv=5)
print(f"\n📊 Cross-validation scores: {cv_scores}")
print(f"📊 Mean CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

# Classification report
print(f"\n📋 Classification Report:")
print(classification_report(y_test, y_pred_best, target_names=['Real', 'Fake']))

# Confusion Matrix
print(f"\n📊 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_best))
print("   [True Real, False Fake]")
print("   [False Real, True Fake]")

# Feature importance (if available)
if hasattr(best_model, 'feature_importances_'):
    print(f"\n📈 Feature Importance (top 5):")
    importance_df = pd.DataFrame({
        'feature': features,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False).head(5)
    for _, row in importance_df.iterrows():
        print(f"   • {row['feature']}: {row['importance']:.3f}")

print("\n" + "="*60)
print("✅ TRAINING COMPLETE!")
print("="*60)