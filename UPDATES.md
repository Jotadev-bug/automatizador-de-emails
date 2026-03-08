# V2 Architecture Upgrades: Enterprise-Ready Email Automation

This document outlines the technical roadmap to scale the current Minimum Viable Product (MVP) into a robust, production-ready system. The focus shifts from basic functionality to high availability, data observability, advanced NLP capabilities, and strict security standards suitable for an enterprise environment (deployment target: Raspberry Pi).

## 1. Executive Dashboard (Data Observability)
Replacing terminal outputs with a real-time web interface to visualize system performance and business ROI (Return on Investment).

* **Technology Stack:** `Streamlit` (Frontend), `pandas` (Data manipulation), `plotly` (Interactive charts).
* **Technical Implementation:**
  * **Data Caching:** Implement `@st.cache_data` to prevent querying the database on every UI refresh, optimizing RAM usage on the host device.
  * **Key Metrics (KPIs):**
    * Total emails processed (Daily/Weekly/Monthly).
    * Automation accuracy (based on user feedback loops).
    * Estimated human hours saved (Calculated as `Emails_Processed * 2 minutes`).
  * **Interactive UI:**
    * Sidebar for date filtering and confidence threshold adjustments.
    * Data grid showing recent routing decisions with color-coded tags based on the predicted class.

## 2. Generative AI Integration (Agentic Workflows)
Expanding the system's capabilities beyond simple classification to active task execution using Large Language Models (LLMs).

* **Technology Stack:** `OpenAI API` (gpt-4o-mini for cost-efficiency) or `Google Gemini API`.
* **Technical Implementation:**
  * **Structured Data Extraction:** For emails classified as "Invoices", prompt the LLM to output a strictly formatted JSON object extracting `{"Vendor_Name", "Invoice_Amount", "Due_Date", "IBAN"}`.
  * **Smart Thread Summarization:** For "Urgent/Support" emails exceeding 500 words, generate a concise 3-bullet-point summary.
  * **Auto-Drafting & Webhooks:** Integrate with the Gmail API's `drafts.create` endpoint to automatically generate polite response drafts for client inquiries. Trigger a Slack/Telegram webhook alerting the CEO that a draft is ready for review.

## 3. Persistent Logging & State Management
Ensuring system accountability, debugging capabilities, and data retention without relying on volatile memory.



* **Technology Stack:** `SQLite3`, `SQLAlchemy` (ORM).
* **Technical Implementation:**
  * **Schema Design (`logs.db`):**
    * `id` (Primary Key, Auto-increment)
    * `message_id` (String, Unique constraint to prevent duplicate processing)
    * `timestamp` (Datetime)
    * `sender` (String)
    * `predicted_class` (Integer/String)
    * `confidence_score` (Float)
    * `action_taken` (String)
  * **Indexing:** Create indexes on `timestamp` and `predicted_class` to ensure fast query execution for the Streamlit dashboard.
  * **Data Retention Policy:** Implement a scheduled cleanup job to purge logs older than 90 days, preventing storage exhaustion on the Raspberry Pi's SD card.

## 4. Containerization & Continuous Deployment
Packaging the entire application ecosystem to ensure environment consistency and automated recovery.



* **Technology Stack:** `Docker`, `Docker Compose`.
* **Technical Implementation:**
  * **Multi-stage Dockerfile:** Build a lightweight image using `python:3.10-slim`. Separate the dependency installation phase from the final runtime environment to minimize the image footprint (critical for ARM architectures like Raspberry Pi).
  * **Volume Mapping:** Mount a local directory to the container's `/app/data` to ensure the SQLite database and the trained `.joblib` ML models persist across container restarts.
  * **Orchestration (`docker-compose.yml`):** Define two services: `classifier_daemon` (background worker) and `streamlit_dashboard` (web UI).
  * **Resilience:** Set the `restart: always` policy so the system automatically boots up if the Raspberry Pi loses power or the script crashes.

## 5. Security & Authentication (Enterprise Standard)
Hardening the application to handle sensitive corporate communications safely.

* **Technology Stack:** `python-dotenv`, `OAuth 2.0`.
* **Technical Implementation:**
* **Secrets Management:** Remove all hardcoded credentials. Enforce the use of a `.env` file (excluded via `.gitignore`) to inject API keys and database paths as environment variables.
* **Modern Authentication:** Migrate from basic IMAP App Passwords to secure OAuth 2.0 token-based authentication (using Google Cloud Console credentials) to comply with modern IT security policies.