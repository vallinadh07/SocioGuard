from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pandas as pd


class URLMLAnalyzer:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000
        )
        self.model = LogisticRegression(max_iter=1000)

    def train(self, path):
        df = pd.read_csv(path)

        # 🔥 FIX (important)
        df["url"] = df["url"].fillna("").str.lower()

        X = self.vectorizer.fit_transform(df["url"])
        y = df["label"]

        self.model.fit(X, y)

    def predict(self, url):
        X = self.vectorizer.transform([url.lower()])

        pred = self.model.predict(X)[0]
        prob = self.model.predict_proba(X)[0]

        confidence = max(prob)

        return pred, confidence