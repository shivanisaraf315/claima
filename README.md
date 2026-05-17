# 🛡️ CLAIMA
### Cognitive Line Agent for Insurance Management & Automation

> An AI-powered multi-agent system that automates insurance document processing — built with Python, Google Gemini AI, and Streamlit.

---

## 📌 What It Does

CLAIMA automates the entire insurance submission intake pipeline:

| Step | Agent | What Happens |
|------|-------|-------------|
| 1 | Parser Agent | Reads uploaded PDF, extracts raw text |
| 2 | Extractor Agent | Sends text to Gemini AI, gets structured fields |
| 3 | Validator Agent | Checks all required fields are present |
| 4 | Classifier Agent | Identifies: Auto / Property / General Liability |
| 5 | Router Agent | Assigns submission ID, priority, and routes to queue |

---

## 🚀 How to Run

### Step 1 — Clone the repo
```bash
git clone https://github.com/sarafshivani315/claima.git
cd claima
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Add your Gemini API key
Create a `.env` file in the root folder:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Get a free key at: https://aistudio.google.com

### Step 4 — Generate sample documents
```bash
python create_sample_docs.py
```

### Step 5 — Run the app
```bash
streamlit run ui/app.py
```

Open your browser at `http://localhost:8501`

---

## 🗂 Project Structure

```
CLAIMA/
├── agents/
│   ├── parser_agent.py       # PDF text extraction
│   ├── extractor_agent.py    # Gemini AI field extraction
│   ├── validator_agent.py    # Completeness validation
│   ├── classifier_agent.py   # Line of business classification
│   └── router_agent.py       # Queue routing and storage
├── data/
│   ├── submissions.json      # All processed submissions
│   └── queues.json           # Underwriting queues
├── sample_docs/              # Test PDF documents
├── ui/
│   └── app.py                # Streamlit web interface
├── chatbot.py                # AI status chatbot
├── main.py                   # Pipeline orchestrator
└── requirements.txt
```

---

## 🛠 Tech Stack

- **Python** — Core language
- **Google Gemini API** — AI document understanding and chatbot
- **pdfplumber** — PDF text extraction
- **Streamlit** — Web UI
- **python-dotenv** — Secure API key management
- **JSON** — Lightweight data storage

**All tools are 100% free.**

---

## 📋 Features

- Upload PDF insurance documents via web UI
- Automatic extraction of 15+ insurance fields
- Validation with missing field detection
- Auto-classification into 3 lines of business
- Priority-based routing (High / Medium / Low)
- Real-time queue management dashboard
- AI chatbot for submission status queries
- Full submission history with filters

---

## 💬 Sample Chatbot Queries

- *"What is the status of CLAIMA-20241215-143022?"*
- *"Is the submission for Rajesh Kumar complete?"*
- *"How many high priority submissions are pending?"*
- *"Which team is handling the property submission?"*

---

Built as a major academic project demonstrating Generative AI, multi-agent architecture, and intelligent workflow automation in real-world insurance operations.