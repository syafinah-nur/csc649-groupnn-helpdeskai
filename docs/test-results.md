# UFix  Testing and Evaluation

# 1. Testing Objective
We tested how well the chatbot finds the right FAQ, how relevant its answers are, how well it fits the UiTM IT domain, whether the interface works, and how it handles unclear questions, unsupported questions, and errors.

# 2. Testing Configuration
 Dataset: 48 Q&A pairs
 Retrieval method: TFIDF and cosine similarity
 Stop word filtering: English, retaining important negative words
 Text preprocessing: Keyword normalisation
 High confidence threshold: 0.45
 Low confidence threshold: 0.25
 Ambiguity margin: 0.10
 Adaptive suggestion factor: 0.6
 Maximum FAQ suggestions: 4
 LLM provider: Google Gemini API
 Model: Gemini 3.5 Flash
 Temperature: 0.2
 Maximum output tokens: 1024
 User interface: Streamlit
 Automated chatbot testing: Python test and mock

# 3. Retrieval Testing Results

# Experiment 1: Original Dataset (33 FAQs)
 Total tests: 11
 Passed: 11
 Failed: 0
 Pass rate: 100%

# Experiment 2: Expanded Dataset (48 FAQs)
 Total tests: 18
 Passed: 17
 Failed: 1
 Pass rate: 94.44%

# Experiment 3: Combined Question and Answer Retrieval
 Total tests: 18
 Passed: 10
 Failed: 8
 Pass rate: 55.56%

# Experiment 4: Retrieval After Dataset Refinement
 Total tests: 18
 Passed: 18
 Failed: 0
 Pass rate: 100%

# Experiment 5: Retrieval After Normalisation and Ambiguity Improvements
 Total tests: 18
 Passed: 18
 Failed: 0
 Pass rate: 100%

The final implementation retained question only retrieval while introducing keyword normalisation, FAQ ranking, service recognition and ambiguity detection.

# 4. Final Retrieval Performance
 Answer: 13/13 passed
 Clarification: 1/1 passed
 Fallback: 3/3 passed
 Validation: 1/1 passed
 Overall result: 18/18 passed (100%)

These results measure FAQ retrieval and confidence classification rather than the complete chatbot response.

# 5. Automated Chatbot Behaviour Testing

A separate test script was developed to evaluate the chatbot's decision making and response handling.

The following behaviours were tested:

 Input validation
 Greeting handling
 Acknowledgement handling
 WiFi spelling variations
 Login spelling variations
 Broad keyword clarification
 Supported service recognition
 All 48 exact FAQ questions
 Unsupported questions
 FAQ suggestion limits
 Suggestions originating from the dataset
 Empty LLM response handling
 API failure handling

# Test Results
 Total test methods: 13
 Passed: 13
 Failed: 0
 Pass rate: 100%
 Execution time: 0.921 seconds

We mocked the Gemini API during these tests. This let us test chatbot behaviour without using API quota or depending on the external API being available.

These tests do not measure whether live Gemini responses are factually correct

# 6. Overall Automated Testing Results
 Retrieval test cases: 18/18 passed
 Chatbot test methods: 13/13 passed
 Combined total: 31/31 passed
 Overall pass rate: 100%

The chatbot test methods also contain many subtests covering different inputs and FAQ questions

# 7. Manual Chatbot Evaluation

The first round of manual testing passed all 10 cases. The chatbot replies matched the FAQ answers. We ran more manual tests after expanding the dataset and improving the retrieval mechanism.

Manual testing showed several weaknesses that the original retrieval tests did not catch

# Successful Responses
 Recognising WiFi spelling variations.
 Suggesting related FAQ questions for broad service names.
 Providing clarification for ambiguous password related questions.
 Returning relevant answers for specific IT questions.
 Returning fallback responses for unsupported inputs.

# Unsuccessful or Limited Responses
 The input "pass" was not recognised as shorthand for password.
 Responses such as "yes" and "no" were not interpreted using previous messages.
 The input "licensing" returned a fallback response despite related information being available in the dataset.
 Some broad inputs produced incomplete or weakly related FAQ suggestions.

These observations were used to identify the remaining system limitations.

# 8. Frontend Testing
 User interface: Pass
 Backend connection: Pass
 Greeting handling: Pass
 Response generation: Pass
 Clear conversation: Pass
 API failure fallback: Pass

The sidebar was simplified to display common IT topics instead of listing every supported service. 

# 9. Problems We Found and Fixed

# 9.1 Wrong FAQ Matches
Common English words like "how" and "do" caused the chatbot to match the wrong FAQ. We added English stopword filtering to reduce this problem.

# 9.2 Eduroam Question Failed
The original FAQ question did not contain the word "eduroam", so the chatbot matched it to the wrong campus WiFi FAQ. We tried searching both the question and the answer, but this made results worse. We kept questiononly retrieval and refined the FAQ question to include the word "eduroam".

# 9.3 Gemini API Errors
The Gemini API sometimes returned 503 errors and failed to answer. We added a fallback that returns the relevant FAQ answer directly when the API is unavailable. Empty Gemini responses are also handled by returning the original FAQ answer.

# 9.4 Inconsistent Keyword Recognition
Different forms of the same keyword, such as "wifi", "WiFi" and "wi fi", previously produced inconsistent responses. We introduced keyword normalisation for both FAQ questions and user inputs to improve consistency.

# 9.5 Generic Clarification Responses
Broad inputs previously received generic clarification messages without useful guidance. We introduced dynamic FAQ suggestions that retrieve related questions directly from the custom dataset.

# 9.6 Ambiguous HighConfidence Matches
Some broad questions received direct answers even though the user's intention was unclear. We introduced ambiguity detection based on meaningful words, retrieval confidence and the similarity difference between competing FAQ matches.

# 9.7 Limited Automated Testing
The original automated tests only evaluated FAQ retrieval and confidence classification. We added a separate chatbot testing script to evaluate input handling, clarification, service recognition, fallback responses and API failure handling.

# 10. System Limitations
 The knowledge base only has 48 Q&A pairs.
 TFIDF matches words rather than fully understanding their meaning.
 New or unusual questions may retrieve the wrong FAQ.
 Recognition of spelling mistakes, abbreviations and synonyms is limited.
 FAQ suggestions may be incomplete or weakly related.
 The chatbot processes one question at a time.
 Chat history is displayed on screen but is not used as context for subsequent questions.
 Short followup responses such as "yes" and "no" cannot be interpreted in context.
 These test results do not cover every possible user question.

# 11. Future Improvements
 Expand the FAQ dataset to cover more UiTM IT services.
 Implement session based conversation memory.
 Improve multilingual retrieval for English and Malay.
 Support multiple questions within a single message.
 Improve FAQ suggestion relevance and coverage.
