# Technical Roadmap: AI-Powered Email Automation MVP

This document outlines the end-to-end technical roadmap for developing a local Minimum Viable Product (MVP) of an intelligent email routing system. The architecture relies on Python, leveraging IMAP/SMTP protocols for I/O operations and a classical NLP pipeline for text classification.



## Phase 1: Synthetic Data Engineering & Environment
To avoid privacy breaches during development, we will build a robust synthetic dataset simulating a real corporate inbox environment.

* **1.1 Environment & Dependency Management:**
  * Initialize a virtual environment (`venv` or `Conda`).
  * Core dependencies: `scikit-learn`, `pandas`, `nltk` (or `spaCy`), `Faker`, `imap-tools`, `beautifulsoup4`, `python-dotenv`.
* **1.2 Data Generation Engine (`Faker`):**
  * Develop a Python module using `Faker` to generate a `pandas` DataFrame.
  * Define 3 core target classes and inject domain-specific vocabulary:
    * `Class 0 (Invoices)`: Synthesize company names, IBANs, amounts, and attach fake `.pdf` extensions in the text.
    * `Class 1 (Urgent/Support)`: Inject keywords reflecting high-priority issues, system outages, or angry client semantics.
    * `Class 2 (Noise/Newsletters)`: Generate marketing copy, unsubscribe links, and promotional jargon.
  * **Goal:** Generate a balanced dataset of 1,000+ records and export to `data/synthetic_emails.csv`.
* **1.3 SMTP Injection Script:**
  * Build a script using `smtplib` and `email.mime` modules.
  * Construct Multipart MIME messages (simulating real email structures).
  * Automate the dispatch of a random subset (e.g., 50 emails) to a dedicated test inbox (`my_test_inbox@gmail.com`) via Google's SMTP server using App Passwords.

## Phase 2: IMAP Ingestion & Text Preprocessing
Develop the data ingestion layer to fetch and normalize raw email data.



* **2.1 Connection Protocol:**
  * Implement `imap-tools` to establish a secure SSL/TLS connection.
  * Target the `INBOX` folder and filter strictly for `UNSEEN` emails using IMAP search criteria.
* **2.2 Parsing & Extraction:**
  * Extract metadata: `Message-ID`, `Sender`, `Date`, `Subject`.
  * Handle multipart emails: Extract the payload, prioritizing `text/plain`. If only `text/html` is available, use `BeautifulSoup` to strip HTML tags and extract raw text.
* **2.3 NLP Preprocessing Pipeline:**
  * Implement a robust cleaning function using `re` and `nltk`:
    * Lowercasing and punctuation removal.
    * Tokenization (splitting text into individual words).
    * Stop-word removal (filtering out "the", "and", "is", etc.).
    * Stemming or Lemmatization (reducing words to their root form, e.g., "running" $\rightarrow$ "run") to reduce feature space dimensionality.

## Phase 3: The ML Pipeline (Feature Engineering & Classification)
Design, train, and serialize the Natural Language Processing model.

* **3.1 Feature Extraction (Vectorization):**
  * Utilize `scikit-learn`'s `TfidfVectorizer` to convert unstructured text into a numerical matrix.
  * *Technical Note:* TF-IDF (Term Frequency-Inverse Document Frequency) evaluates how relevant a word is to a document in a collection. It is calculated as:
    $$TF\text{-}IDF(t, d) = TF(t, d) \times \log\left(\frac{N}{DF(t)}\right)$$
    Where $t$ is the term, $d$ is the document, $N$ is the total number of documents, and $DF(t)$ is the number of documents containing the term $t$.
* **3.2 Model Selection & Training:**
  * Split the dataset (`train_test_split`) using an 80/20 ratio.
  * Instantiate a `MultinomialNB` (Naive Bayes) or `LinearSVC` (Support Vector Classifier). Linear models perform exceptionally well in high-dimensional sparse text data.
* **3.3 Evaluation Metrics:**
  * Generate a `classification_report` analyzing Precision, Recall, and the F1-Score for each class.
  * Plot a Confusion Matrix to analyze false positives (e.g., ensuring an invoice isn't misclassified as noise).
* **3.4 Model Serialization:**
  * Persist the trained model and the fitted `TfidfVectorizer` to disk using `joblib` so they can be loaded into memory without retraining during live execution.

## Phase 4: State Management & Automated Execution
Tie the I/O operations and the ML model together in a continuous execution loop.

* **4.1 Execution Logic:**
  * Load the `joblib` artifacts into memory.
  * Fetch `UNSEEN` emails $\rightarrow$ Pass through the Preprocessing Pipeline $\rightarrow$ Vectorize $\rightarrow$ Predict class.
* **4.2 Action Router (IMAP Flags & Moves):**
  * Class 0 (Invoices): Call `mailbox.move(uid, '1_INVOICES')`.
  * Class 1 (Urgent): Apply `\Flagged` (Starred) flag and move to '2_URGENT'.
  * Class 2 (Noise): Apply `\Seen` flag and call `mailbox.delete(uid)` or move to Trash.
* **4.3 Logging & Error Handling:**
  * Implement Python's `logging` module to record timestamps, `Message-ID`s processed, predicted classes, and confidence scores.
  * Wrap network operations in `try/except` blocks to handle unexpected IMAP connection drops.

## Phase 5: Daemonization & Demonstration
Make the MVP run autonomously and prepare the pitch.

* **5.1 Local Scheduling:**
  * Refactor the execution loop into a standalone script.
  * Use the `schedule` Python library or a local `cron` job (Linux/macOS) to trigger the script every 5 minutes.
* **5.2 Showcase Production:**
  * Screen-record the terminal logging the predictions (`[INFO] Email UID 145 -> Predicted: INVOICE (98% confidence) -> Moved to folder`).
  * Show the immediate reflection of these actions in the Gmail Web UI.