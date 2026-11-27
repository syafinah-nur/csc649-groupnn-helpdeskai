import sys
from collections import Counter

import pandas as pd

from src.retrieval import FAQRetriever


#Labels must match Expected_Behaviour in tests/test_questions.csv.
BEHAVIOUR_VALIDATION = "Validation"
BEHAVIOUR_FALLBACK = "Fallback"
BEHAVIOUR_CLARIFICATION = "Clarification"
BEHAVIOUR_ANSWER = "Answer"


def run_tests():
    retriever = FAQRetriever()
    tests = pd.read_csv("tests/test_questions.csv").fillna("")
    dataset = pd.read_csv("data/it_faq.csv")

    required = {"Test_ID", "Category", "Question", "Expected_FAQ", "Expected_Behaviour"}
    missing = required - set(tests.columns)
    if missing:
        raise ValueError(f"test_questions.csv missing columns: {missing}")
    if tests.empty:
        raise ValueError("test_questions.csv contains no test cases.")

    # Validate every Expected_FAQ against the dataset
    valid_questions = set(dataset["Question"])
    for expected_faq in tests["Expected_FAQ"]:
        if expected_faq and expected_faq not in valid_questions:
            raise ValueError(f"Expected FAQ not found in dataset: {expected_faq!r}")

    passed_count = 0
    behaviour_total = Counter()
    behaviour_passed = Counter()

    for _, test in tests.iterrows():
        question = str(test["Question"]).strip()
        expected_faq = str(test["Expected_FAQ"]).strip()
        expected_behaviour = str(test["Expected_Behaviour"]).strip()

        result = retriever.search(question)

        if not question:
            actual_behaviour = BEHAVIOUR_VALIDATION
        elif result is None:
            actual_behaviour = BEHAVIOUR_FALLBACK
        elif result["confidence"] == "low":
            actual_behaviour = BEHAVIOUR_CLARIFICATION
        else:
            actual_behaviour = BEHAVIOUR_ANSWER

        actual_faq = result["question"] if result else ""
        similarity = result["similarity"] if result else None

        passed = actual_behaviour == expected_behaviour
        if expected_faq:
            passed = passed and actual_faq == expected_faq

        behaviour_total[expected_behaviour] += 1
        if passed:
            passed_count += 1
            behaviour_passed[expected_behaviour] += 1

        print(f"\nTest: {test['Test_ID']}")
        print(f"Category: {test['Category']}")
        print(f"Question: {question}")
        print(f"Expected FAQ: {expected_faq}")
        print(f"Retrieved FAQ: {actual_faq}")
        if similarity is not None:
            print(f"Similarity: {similarity:.3f}")
        else:
            print("Similarity: N/A (no accepted match)")
        print(f"Expected behaviour: {expected_behaviour}")
        print(f"Actual behaviour: {actual_behaviour}")

        if expected_faq:
            expected_answer = dataset.loc[
                dataset["Question"] == expected_faq, "Answer"
            ].iloc[0]
            print(f"Expected answer: {expected_answer}")

        print(f"Result: {'PASS' if passed else 'FAIL'}")

    total = len(tests)
    rate = passed_count / total * 100

    print("\n--- Test Summary ---")
    print(f"Total tests: {total}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {total - passed_count}")
    print(f"Pass rate: {rate:.2f}%")

    print("\n--- By Behaviour ---")
    for behaviour, count in behaviour_total.items():
        print(f"{behaviour}: {behaviour_passed[behaviour]}/{count}")

    if passed_count < total:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()