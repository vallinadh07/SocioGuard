import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs('backend/models', exist_ok=True)

print("="*60)
print("🔬 TRAINING URL SCAM DETECTION ML MODEL")
print("="*60)

# Load dataset
df = pd.read_csv('datasets/raw/scam_url_dataset.csv')
print(f"\n📊 Loaded {len(df)} URL samples")
print(f"   Scam: {(df['is_scam']==1).sum()}, Safe: {(df['is_scam']==0).sum()}")

# Check what columns are available
print(f"\n📋 Available columns: {df.columns.tolist()}")

# Features that exist in your dataset (based on actual columns)
feature_cols = ['url_length', 'num_dots', 'num_slashes', 'has_https', 'has_digits']

# Add any other feature columns if they exist
if 'has_ip' in df.columns:
    feature_cols.append('has_ip')
if 'is_shortened' in df.columns:
    feature_cols.append('is_shortened')

print(f"\n🔍 Using features: {feature_cols}")

X = df[feature_cols]
y = df['is_scam']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"📈 Training set: {len(X_train)} samples")
print(f"📈 Test set: {len(X_test)} samples")

# Train multiple models
print("\n🤖 Training multiple ML models...")

models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'SVM': SVC(kernel='rbf', probability=True, random_state=42)
}

results = {}
best_model = None
best_accuracy = 0

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    results[name] = accuracy
    print(f"   {name}: {accuracy:.2%}")

# Select best model
best_name = max(results, key=results.get)
best_accuracy = results[best_name]
best_model = models[best_name]

print(f"\n🏆 BEST MODEL: {best_name} with {best_accuracy:.2%} accuracy")

# Save model and features
joblib.dump(best_model, 'backend/models/scam_url_model.pkl')
joblib.dump(feature_cols, 'backend/models/scam_url_features.pkl')
print(f"\n💾 Saved {best_name} model to backend/models/")

# Detailed report
print("\n" + "="*60)
print(f"📋 DETAILED REPORT - {best_name}")
print("="*60)

y_pred_best = best_model.predict(X_test)
print("\n📋 Classification Report:")
print(classification_report(y_test, y_pred_best, target_names=['Safe', 'Scam']))

print("\n📊 Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred_best)
print(cm)
print("   [True Safe, False Scam]")
print("   [False Safe, True Scam]")

# Feature importance for tree-based models
if hasattr(best_model, 'feature_importances_'):
    print("\n📈 Feature Importance:")
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    for _, row in importance_df.iterrows():
        print(f"   • {row['feature']}: {row['importance']:.3f}")

print("\n✅ URL ML model training complete!")