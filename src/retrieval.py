import re
import unicodedata

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class FAQRetriever:
    def __init__(
        self,
        csv_path="data/it_faq.csv",
        high_threshold=0.45,
        low_threshold=0.25
    ):
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.ambiguity_margin = 0.10

        # Load and validate the dataset
        self.data = pd.read_csv(csv_path)

        required_columns = {"Question", "Answer"}

        if not required_columns.issubset(self.data.columns):
            raise ValueError(
                "The FAQ dataset must contain Question and Answer columns."
            )

        if self.data.empty:
            raise ValueError("The FAQ dataset is empty.")

        if self.data[["Question", "Answer"]].isna().any().any():
            raise ValueError("The FAQ dataset contains missing values.")

        for column in ["Question", "Answer"]:
            self.data[column] = (
                self.data[column].astype(str).str.strip()
            )

            if self.data[column].eq("").any():
                raise ValueError(
                    f"The FAQ dataset contains empty {column} values."
                )

        # Service categories and recognised aliases
        self.services = {
            "wifi": (
                "wifi", "campus wifi", "eduroam",
                "wireless network"
            ),
            "ufuture": (
                "ufuture", "u future"
            ),
            "istudent": (
                "istudent", "istudent portal",
                "sims", "simsweb"
            ),
            "google workspace": (
                "google workspace", "gmail",
                "google drive"
            ),
            "password reset": (
                "password reset", "forgot password",
                "reset password"
            ),
            "vpn": (
                "vpn", "vpn access"
            ),
            "digital student id": (
                "digital student id", "student id",
                "ucms"
            ),
            "ict helpdesk": (
                "ict helpdesk", "helpdesk", "units",
                "ict helpdesk and reporting"
            ),
            "university software and licensing": (
                "university software and licensing",
                "university software", "software licensing",
                "software license", "microsoft 365",
                "office 365"
            ),
            "digital library and research tools": (
                "digital library and research tools",
                "digital library", "library",
                "research tools"
            ),
            "basic computer troubleshooting": (
                "basic computer troubleshooting",
                "computer troubleshooting", "computer",
                "laptop", "usb"
            )
        }

        self.service_keywords = {
            "wifi": (
                "wifi", "eduroam", "wireless"
            ),
            "ufuture": (
                "ufuture",
            ),
            "istudent": (
                "istudent", "sims", "simsweb"
            ),
            "google workspace": (
                "google workspace", "gmail", "google drive"
            ),
            "password reset": (
                "password",
            ),
            "vpn": (
                "vpn",
            ),
            "digital student id": (
                "digital student id", "ucms"
            ),
            "ict helpdesk": (
                "helpdesk", "ict", "units"
            ),
            "university software and licensing": (
                "software", "license", "licensing",
                "microsoft 365", "office 365"
            ),
            "digital library and research tools": (
                "library", "research"
            ),
            "basic computer troubleshooting": (
                "computer", "laptop", "usb",
                "overheating", "wireless network"
            )
        }

        self.aliases = {}

        for service, aliases in self.services.items():
            for alias in aliases:
                self.aliases[self.normalise(alias)] = service

        # Normalise FAQ questions before indexing
        self.normalised_questions = (
            self.data["Question"].apply(self.normalise)
        )

        # Keep important negative words
        stop_words = set(
            TfidfVectorizer(stop_words="english")
            .get_stop_words()
        )

        stop_words.difference_update({
            "not", "no", "cannot", "without"
        })

        self.vectorizer = TfidfVectorizer(
            stop_words=sorted(stop_words)
        )

        self.faq_vectors = self.vectorizer.fit_transform(
            self.normalised_questions
        )

    @staticmethod
    def normalise(text):
        text = unicodedata.normalize(
            "NFKC", str(text)
        ).lower()

        text = text.replace("’", "'")

        text = re.sub(
            r"[\u2010-\u2015\u2212]", "-", text
        )

        replacements = {
            r"\bwi[\s-]*fi\b": "wifi",
            r"\bu[\s-]*future\b": "ufuture",
            r"\bi[\s-]*student\b": "istudent",
            r"\bedu[\s-]*roam\b": "eduroam",
            r"\blog[\s-]*in\b": "login",
            r"\bsign[\s-]*in\b": "login",

            r"\bpass[\s-]*word\b": "password",
            r"\buser[\s-]*name\b": "username",

            r"\bsubjects\b": "subject",
            r"\bcourses\b": "course",
            r"\bpasswords\b": "password",
            r"\baccounts\b": "account",
            r"\bassignments\b": "assignment",
            r"\bquizzes\b": "quiz",
            r"\bfiles\b": "file",
            r"\berrors\b": "error",
            r"\bdevices\b": "device",
            r"\blicences\b": "license",
            r"\blicence\b": "license",
            r"\blicenses\b": "license",

            r"\bnot appearing\b": "missing",
            r"\bnot showing(?: up)?\b": "missing",
            r"\bnot visible\b": "missing",

            r"\bcan not\b": "cannot",
            r"\bcan't\b": "cannot",
            r"\bunable to\b": "cannot",
            r"\bdon't\b": "do not",
            r"\bdoesn't\b": "does not",
            r"\bisn't\b": "is not",

            r"\bforgotten\b": "forgot",
            r"\boff[\s-]*campus\b": "off campus",
            r"\bon[\s-]*campus\b": "on campus"
        }

        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)

        text = re.sub(r"[^\w\s]", " ", text)

        return " ".join(text.split())

    @staticmethod
    def contains_phrase(text, phrase):
        return bool(
            re.search(
                r"\b" + re.escape(phrase) + r"\b",
                text
            )
        )

    def get_service(self, user_question):
        return self.aliases.get(
            self.normalise(user_question)
        )

    def is_service_query(self, user_question):
        return self.get_service(user_question) is not None

    def get_similarities(self, user_question):
        normalised = self.normalise(user_question)

        user_vector = self.vectorizer.transform(
            [normalised]
        )

        return cosine_similarity(
            user_vector,
            self.faq_vectors
        ).flatten()

    def rank(self, user_question):
        if not user_question or not user_question.strip():
            return []

        similarities = self.get_similarities(
            user_question
        )

        ranked_indices = similarities.argsort()[::-1]

        results = []

        for index in ranked_indices:
            score = float(similarities[index])

            if score <= 0:
                break

            results.append({
                "question": self.data.iloc[index]["Question"],
                "answer": self.data.iloc[index]["Answer"],
                "similarity": score,
                "confidence": (
                    "high"
                    if score >= self.high_threshold
                    else "low"
                )
            })

        return results

    def search(self, user_question):
        results = self.rank(user_question)

        if not results:
            return None

        best = results[0]

        if best["similarity"] < self.low_threshold:
            return None

        return best

    def is_exact_match(self, user_question):
        normalised = self.normalise(user_question)

        return normalised in self.normalised_questions.values

    def is_ambiguous(self, user_question, results):
        normalised = self.normalise(user_question)

        if self.is_service_query(user_question):
            return True

        if self.is_exact_match(user_question):
            return False

        # Use meaningful indexed words, not total sentence length
        analyser = self.vectorizer.build_analyzer()
        meaningful_words = set(analyser(normalised))

        if len(meaningful_words) <= 2:
            return True

        if not results:
            return False

        if results[0]["similarity"] < self.high_threshold:
            return True

        # Compare competing FAQ matches
        if len(results) >= 2:
            best_score = results[0]["similarity"]
            second_score = results[1]["similarity"]

            if (
                second_score >= self.low_threshold
                and best_score - second_score
                < self.ambiguity_margin
            ):
                return True

        return False

    def suggest(self, user_question, limit=4):
        if (
            not user_question
            or not user_question.strip()
            or limit <= 0
        ):
            return []

        results = self.rank(user_question)
        service = self.get_service(user_question)

        suggestions = []
        seen = set()

        # Retrieve service-specific questions
        if service:
            keywords = self.service_keywords[service]

            candidates = [
                item["question"] for item in results
            ]

            candidates.extend(
                self.data["Question"].tolist()
            )

            for question in candidates:
                question_text = self.normalise(question)

                matched = any(
                    self.contains_phrase(
                        question_text,
                        self.normalise(keyword)
                    )
                    for keyword in keywords
                )

                if matched and question not in seen:
                    suggestions.append(question)
                    seen.add(question)

                if len(suggestions) >= limit:
                    return suggestions

            return suggestions

        if not results:
            return []

        best_score = results[0]["similarity"]

        minimum_score = max(
            self.low_threshold * 0.6,
            best_score * 0.6
        )

        for result in results:
            if result["similarity"] < minimum_score:
                break

            question = result["question"]

            if question not in seen:
                suggestions.append(question)
                seen.add(question)

            if len(suggestions) >= limit:
                break

        return suggestions