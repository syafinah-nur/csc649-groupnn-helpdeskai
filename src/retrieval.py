import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class FAQRetriever:
    def __init__(self, csv_path="data/it_faq.csv",
                 high_threshold=0.45, low_threshold=0.25):

        self.high_threshold = high_threshold
        self.low_threshold = low_threshold

        self.data = pd.read_csv(csv_path)
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.faq_vectors = self.vectorizer.fit_transform(
            self.data["Question"]
        )

    def search(self, user_question):
        # Skip empty input.
        if not user_question or not user_question.strip():
            return None

        # Turn user question into a TF-IDF vector.
        user_vector = self.vectorizer.transform([user_question])

        # Compare with FAQ question.
        similarities = cosine_similarity(
            user_vector, self.faq_vectors
        ).flatten()

        # Take the closest match.
        best_index = int(similarities.argmax())
        best_score = float(similarities[best_index])

        # If it's too weak, reject.
        if best_score < self.low_threshold:
            return None

        # high match
        confidence = (
            "high" if best_score >= self.high_threshold
            else "low"
        )

        return {
            "question": self.data.iloc[best_index]["Question"],
            "answer": self.data.iloc[best_index]["Answer"],
            "similarity": best_score,
            "confidence": confidence
        }