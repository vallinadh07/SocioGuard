import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs('backend/models', exist_ok=True)

print("="*60)
print("🔬 TRAINING TEXT SCAM DETECTION ML MODEL")
print("="*60)

# Load dataset
df = pd.read_csv('datasets/raw/scam_text_dataset.csv')
print(f"\n📊 Loaded {len(df)} text samples")
print(f"   Scam: {(df['is_scam']==1).sum()}, Safe: {(df['is_scam']==0).sum()}")

# Convert text to features
print("\n🔍 Converting text to TF-IDF features...")
vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
X = vectorizer.fit_transform(df['text'])
y = df['is_scam']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"📈 Training set: {X_train.shape[0]} samples")
print(f"📈 Test set: {X_test.shape[0]} samples")

# Train multiple models
print("\n🤖 Training multiple ML models...")

models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Naive Bayes': MultinomialNB()
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

# Save model and vectorizer
joblib.dump(best_model, 'backend/models/scam_text_model.pkl')
joblib.dump(vectorizer, 'backend/models/scam_text_vectorizer.pkl')
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

# Cross-validation
cv_scores = cross_val_score(best_model, X_train, y_train, cv=5)
print(f"\n📊 Cross-validation scores: {cv_scores}")
print(f"📊 Mean CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

print("\n✅ Text ML model training complete!")