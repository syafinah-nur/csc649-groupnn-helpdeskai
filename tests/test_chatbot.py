import os
import unittest

from unittest.mock import patch, MagicMock

from src.chatbot import (
    UFix,
    INVALID_INPUT_MSG,
    NO_ANSWER_MSG
)


class TestChatbot(unittest.TestCase):

    def setUp(self):
        env_patch = patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "test-key"}
        )

        client_patch = patch(
            "src.chatbot.genai.Client"
        )

        env_patch.start()
        mock_client = client_patch.start()

        self.addCleanup(env_patch.stop)
        self.addCleanup(client_patch.stop)

        self.bot = UFix()

        self.mock_generate = (
            mock_client.return_value
            .models.generate_content
        )

        self.mock_generate.return_value = MagicMock(
            text="Generated FAQ answer."
        )

    def assertClarification(self, question):
        response = self.bot.chat(question)

        self.assertTrue(
            response.startswith(
                "What specifically do you need help with?"
            )
            or response.startswith(
                "Could you provide more details"
            ),
            msg=f"Unexpected response: {response}"
        )

        self.mock_generate.assert_not_called()

    def test_invalid_input(self):
        for question in ["", "   ", "???", None]:
            with self.subTest(question=question):
                self.assertEqual(
                    self.bot.chat(question),
                    INVALID_INPUT_MSG
                )

        self.mock_generate.assert_not_called()

    def test_greetings(self):
        for question in ["Hi", "Hello!", "Salam"]:
            with self.subTest(question=question):
                self.assertIn(
                    "Hello! I'm UFix",
                    self.bot.chat(question)
                )

        self.mock_generate.assert_not_called()

    def test_acknowledgements(self):
        self.assertIn(
            "You're welcome",
            self.bot.chat("Thank you")
        )

        self.mock_generate.assert_not_called()

    def test_wifi_variations(self):
        for question in ["wifi", "Wi-Fi", "wi fi"]:
            with self.subTest(question=question):
                self.assertClarification(question)

        self.assertEqual(
            self.bot.chat("wifi"),
            self.bot.chat("Wi-Fi")
        )

        self.assertEqual(
            self.bot.chat("wifi"),
            self.bot.chat("wi fi")
        )

    def test_login_variations(self):
        for question in ["login", "log in", "sign in"]:
            with self.subTest(question=question):
                self.assertClarification(question)

    def test_broad_keywords(self):
        questions = [
            "password",
            "assignment",
            "attendance",
            "quiz",
            "missing subject",
            "missing subjects"
        ]

        for question in questions:
            with self.subTest(question=question):
                self.assertClarification(question)

    def test_supported_services(self):
        services = [
            "Campus Wi-Fi",
            "iStudent Portal",
            "UFUTURE",
            "Google Workspace",
            "Password reset",
            "VPN access",
            "Digital Student ID",
            "ICT Helpdesk and Reporting",
            "University Software and Licensing",
            "Digital Library and Research Tools",
            "Basic Computer Troubleshooting"
        ]

        for service in services:
            with self.subTest(service=service):
                self.assertClarification(service)

                self.assertTrue(
                    self.bot.retriever.suggest(service),
                    msg=f"No FAQ suggestions for {service}"
                )

    def test_all_exact_faq_questions(self):
        questions = (
            self.bot.retriever.data["Question"].tolist()
        )

        for question in questions:
            with self.subTest(question=question):
                self.assertEqual(
                    self.bot.chat(question),
                    "Generated FAQ answer."
                )

    def test_unsupported_questions(self):
        questions = [
            "How do I cook fried rice?",
            "xyzabc123"
        ]

        for question in questions:
            with self.subTest(question=question):
                self.assertEqual(
                    self.bot.chat(question),
                    NO_ANSWER_MSG
                )

        self.mock_generate.assert_not_called()

    def test_suggestion_limit(self):
        suggestions = self.bot.retriever.suggest(
            "wifi"
        )

        self.assertGreater(len(suggestions), 0)
        self.assertLessEqual(len(suggestions), 4)

        self.assertEqual(
            len(suggestions),
            len(set(suggestions))
        )

    def test_suggestions_from_dataset(self):
        faq_questions = set(
            self.bot.retriever.data["Question"]
        )

        for query in ["wifi", "login", "ufuture"]:
            with self.subTest(query=query):
                suggestions = (
                    self.bot.retriever.suggest(query)
                )

                for suggestion in suggestions:
                    self.assertIn(
                        suggestion,
                        faq_questions
                    )

    def test_empty_llm_response(self):
        question = (
            self.bot.retriever.data.iloc[0]["Question"]
        )

        expected_answer = (
            self.bot.retriever.data.iloc[0]["Answer"]
        )

        self.mock_generate.return_value.text = "   "

        self.assertEqual(
            self.bot.chat(question),
            expected_answer
        )

    def test_api_failure(self):
        question = (
            self.bot.retriever.data.iloc[0]["Question"]
        )

        expected_answer = (
            self.bot.retriever.data.iloc[0]["Answer"]
        )

        self.mock_generate.side_effect = RuntimeError(
            "Simulated API failure"
        )

        response = self.bot.chat(question)

        self.assertIn(
            "The AI service is currently unavailable",
            response
        )

        self.assertIn(expected_answer, response)


if __name__ == "__main__":
    unittest.main(verbosity=2)