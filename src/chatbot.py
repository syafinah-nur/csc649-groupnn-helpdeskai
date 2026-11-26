import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.retrieval import FAQRetriever
from src.prompts import build_prompt


load_dotenv()


NO_ANSWER_MSG = (
    "Sorry, I don't have information about that "
    "in the UiTM IT helpdesk knowledge base."
)

LOW_CONFIDENCE_MSG = (
    "I'm not fully sure I understood your question. "
    "Could you provide more details about your IT issue?"
)


class UFix:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        self.client = genai.Client(api_key=api_key)
        self.retriever = FAQRetriever()
        self.model = "gemini-3.5-flash"

    def chat(self, user_question):
        # Validate user input
        if not user_question or not user_question.strip():
            return "Please enter a valid question."
        # Handle simple greetings
        greetings = {"hi", "hello", "hey", "hai", "helo", "salam",
                     "assalamualaikum", "good morning",
                     "good afternoon", "good evening"}

        if user_question.strip().lower().rstrip("!? .") in greetings:
            return (
                "Hello! I'm uFix, your UiTM IT helpdesk assistant. "
                "How can I help you today?"
            )
        # Retrieve the relevant FAQ
        result = self.retriever.search(user_question)

        # Handle unsupported questions
        if result is None:
            return NO_ANSWER_MSG

        # Request clarification for weak matches
        if result["confidence"] == "low":
            return LOW_CONFIDENCE_MSG

        # Insert verified FAQ context into the prompt
        prompt = build_prompt(
            user_question,
            result["question"],
            result["answer"]
        )

        # Generate an LLM response
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1024
                )
            )

            return response.text or result["answer"]

        # Handle API failures
        except Exception as e:
            print(f"[UFix] LLM call failed: {e}")

            return (
                "The AI service is currently unavailable. "
                "Here is the relevant FAQ answer:\n\n"
                + result["answer"]
            )