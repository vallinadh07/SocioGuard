import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from utils.preprocessing import clean_text


class MessageAnalyzer:

    def __init__(self):

        self.vectorizer = TfidfVectorizer()

        self.model = LogisticRegression()

        self.trained = False


    def train(self, dataset_path):

        df = pd.read_csv(dataset_path)

        df["clean_text"] = df["text"].apply(clean_text)

        X = self.vectorizer.fit_transform(df["clean_text"])

        y = df["label"]

        self.model.fit(X, y)

        self.trained = True


    def predict(self, message):

        if not self.trained:
            raise Exception("Model not trained")

        cleaned = clean_text(message)

        vector = self.vectorizer.transform([cleaned])

        prediction = self.model.predict(vector)[0]

        confidence = self.model.predict_proba(vector).max()

        return prediction, round(confidence * 100, 2)