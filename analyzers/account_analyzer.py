import pandas as pd
from sklearn.ensemble import RandomForestClassifier


class AccountAnalyzer:

    def __init__(self):

        self.model = RandomForestClassifier()

        self.trained = False


    def train(self, dataset_path):

        df = pd.read_csv(dataset_path)

        X = df[["followers", "following", "posts", "account_age_days"]]

        y = df["label"]

        self.model.fit(X, y)

        self.trained = True


    def predict(self, followers, following, posts, age):

        if not self.trained:
            raise Exception("Model not trained")
        
        data = pd.DataFrame(
            [[followers, following, posts, age]],
            columns=["followers", "following", "posts", "account_age_days"]
        )

        prediction = self.model.predict(data)[0]

        confidence = max(self.model.predict_proba(data)[0])

        return prediction, round(confidence * 100, 2)
