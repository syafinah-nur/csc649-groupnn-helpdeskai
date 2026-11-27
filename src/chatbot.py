import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.retrieval import FAQRetriever
from src.prompts import build_prompt


load_dotenv()


NO_ANSWER_MSG = (
    "Sorry, I don't have information about that in the UiTM IT "
    "helpdesk knowledge base. If your issue is IT-related, "
    "please contact the ICT Helpdesk at "
    "https://units.uitm.edu.my."
)

LOW_CONFIDENCE_MSG = (
    "Could you provide more details about your IT issue? "
    "Please include the service or application you are using "
    "and describe the problem you are experiencing."
)

INVALID_INPUT_MSG = "Please enter a valid question."

GREETING_MSG = (
    "Hello! I'm UFix, your UiTM IT helpdesk assistant. "
    "How can I help you today?"
)

GREETINGS = {
    "hi", "hello", "hey", "hai", "helo",
    "salam", "assalamualaikum",
    "good morning", "good afternoon",
    "good evening"
}

ACKNOWLEDGEMENTS = {
    "thanks", "thank you", "thank you very much",
    "tq", "thx", "terima kasih"
}


class UFix:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        self.client = genai.Client(api_key=api_key)
        self.retriever = FAQRetriever()
        self.model = "gemini-3.5-flash"

    def clarification(self, user_question):
        suggestions = self.retriever.suggest(
            user_question
        )

        if not suggestions:
            return LOW_CONFIDENCE_MSG

        options = "\n".join(
            f"- {question}"
            for question in suggestions
        )

        return (
            "What specifically do you need help with? "
            "Here are some related questions:\n\n"
            + options
            + "\n\nPlease select or describe the issue "
              "that best matches your problem."
        )

    def generate_answer(self, user_question, result):
        faq_answer = result["answer"]

        try:
            prompt = build_prompt(
                user_question,
                result["question"],
                faq_answer
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1024
                )
            )

            answer = (response.text or "").strip()

            if not answer:
                return faq_answer

            return answer

        except Exception as e:
            print(
                f"[UFix] LLM call failed: "
                f"{type(e).__name__}"
            )

            return (
                "The AI service is currently unavailable. "
                "Here is the relevant FAQ answer:\n\n"
                + faq_answer
            )

    def chat(self, user_question):
        # Validate input
        if not isinstance(user_question, str):
            return INVALID_INPUT_MSG

        user_question = user_question.strip()

        if not user_question:
            return INVALID_INPUT_MSG

        normalised = self.retriever.normalise(
            user_question
        )

        if not normalised:
            return INVALID_INPUT_MSG

        # Greetings
        if normalised in GREETINGS:
            return GREETING_MSG

        if normalised in ACKNOWLEDGEMENTS:
            return (
                "You're welcome! Let me know if you "
                "need further IT assistance."
            )

        # Just "vpn" or "wifi" - too vague, ask which FAQ
        if self.retriever.is_service_query(user_question):
            return self.clarification(user_question)

        # find relevant FAQ
        results = self.retriever.rank(user_question)

        if not results:
            return NO_ANSWER_MSG

        best_result = results[0]

        # exact FAQ matches
        if self.retriever.is_exact_match(user_question):
            for result in results:
                if (
                    self.retriever.normalise(result["question"])
                    == normalised
                ):
                    return self.generate_answer(
                        user_question,
                        result
                    )

        # Weak match, suggest related FAQs instead
        if (
            best_result["similarity"]
            < self.retriever.low_threshold
        ):
            suggestions = self.retriever.suggest(
                user_question
            )

            analyser = (
                self.retriever.vectorizer.build_analyzer()
            )

            meaningful_words = set(
                analyser(normalised)
            )

            if len(meaningful_words) <= 2 and suggestions:
                return self.clarification(user_question)

            return NO_ANSWER_MSG

        # Match is unclear, ask the user which one
        if self.retriever.is_ambiguous(
            user_question,
            results
        ):
            return self.clarification(user_question)

        # low-confidence retrieval
        if best_result["confidence"] != "high":
            return self.clarification(user_question)

        return self.generate_answer(
            user_question,
            best_result
        )