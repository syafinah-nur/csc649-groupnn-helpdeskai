# UFix Custom Dataset

## Dataset Overview
The custom dataset contains 48 question-answer pairs covering IT helpdesk services for UiTM students and staff.

## Dataset Structure
- File: it_faq.csv
- Format: CSV
- Total Q&A pairs: 48
- Columns:
  - Question: A common IT question.
  - Answer: The corresponding helpdesk answer.

## Domain Coverage
- Campus Wi-Fi and network connection
- iStudent Portal and SIMS
- UFUTURE
- Google Workspace
- Microsoft 365
- Password recovery
- VPN access
- Digital Student ID
- ICT helpdesk and reporting
- University software and licensing
- Digital library and research tools
- Basic computer troubleshooting

## Data Sources
- UiTM Jabatan Digital – FAQ
  https://digital.uitm.edu.my/index.php/en/muat-turun/faq-spp
- UiTM iCEPS – UFUTURE User Manual
  https://iceps.uitm.edu.my/images/iceps/manual_guideline/manual_ufuture_2026_11092026.pdf
- UiTM Student Portal – FAQ
  https://simsweb.uitm.edu.my/SPORTAL_APP/SPORTAL_LOGIN/faqStudentPortal.pdf
- UiTM Jabatan Digital – Recover Password (Student)
  https://digital.uitm.edu.my/images/faq/recover_password_pelajar.pdf
- UiTM Kad – UCMS Manual Guideline
  https://kad.uitm.edu.my/docs/UCMS%20Manual%20Guideline.pdf
- UiTM Jabatan Digital – Microsoft Azure FAQ
  https://digital.uitm.edu.my/images/faq/MicrosoftAzure.pdf
- UiTM Jabatan Digital – Google Workspace Manual
  https://digital.uitm.edu.my/images/OnlineApps/MANUALGWorkspace.pdf
- UiTM Jabatan Digital – Software FAQ
  https://digital.uitm.edu.my/images/faq/faq_software2.pdf
- UiTM Jabatan Digital – SIMS Password
  https://digital.uitm.edu.my/images/faq/kata_laluan_sims.pdf
- UiTM Jabatan Digital – SIMS Academic FAQ
  https://digital.uitm.edu.my/images/faq/FAQ_SIMS_AKADEMIK.pdf
- UiTM Jabatan Digital – How to Apply for a Cisco Webex Account
  https://digital.uitm.edu.my/images/downloads/info_keeper/Pelbagai/HowToApplyCiscoWebexAccount.pdf
- UiTM Jabatan Digital – Computer Problems FAQ
  https://digital.uitm.edu.my/images/faq/FAQ_MasalahKomputer_Penyelesaiannya.pdf

## Data Preparation
- Collected IT questions and answers relevant to the selected domain.
- Checked each entry for relevance to university IT support.
- Removed duplicates and unsuitable questions.
- Fixed missing values and CSV formatting.
- Refined selected FAQ questions to improve keyword matching.

## Text Preprocessing
The following preprocessing techniques are applied during retrieval:

- Lowercase conversion.
- Unicode and punctuation normalisation.
- Keyword and spelling variation normalisation.
- Selected singular and plural word normalisation.
- English stop-word filtering while retaining important negative words.

These techniques are applied to both FAQ questions and user inputs without changing the original CSV content.

## Dataset Integration
The dataset is loaded and validated using Pandas.
TF-IDF converts the normalised FAQ questions into numerical vectors. Cosine similarity measures the relevance of each FAQ to the user's question.
The chatbot ranks the matching FAQs and evaluates their similarity scores and ambiguity before deciding how to respond.
For clear and relevant questions, the retrieved FAQ question and answer are injected into the Gemini prompt as custom knowledge.
For broad or ambiguous questions, the chatbot suggests related questions directly from the dataset.
If no sufficiently relevant FAQ is found, the chatbot returns a fallback response.
If the Gemini API is unavailable, the chatbot returns the retrieved FAQ answer directly.

## Limitations
- The dataset contains only 48 question-answer pairs.
- The dataset does not cover every UiTM IT issue.
- The questions are primarily written in English.
- Information may become outdated when UiTM updates its systems or policies.
- New questions and alternative wording may not match existing FAQ entries.
- The dataset requires regular review and expansion.

## Future Improvements
- Expand the dataset to cover additional UiTM IT services.
- Include more variations of commonly asked questions.
- Improve English and Malay language coverage.
- Regularly verify FAQ answers against official UiTM sources.