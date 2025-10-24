# 🧠 CognitiveX-145: ClauseWise Legal Document Analyzer

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-orange)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

ClauseWise is an **AI-powered legal document analysis tool** that helps users understand, summarize, and assess contracts quickly and efficiently.
It leverages **IBM Watson NLU**, **IBM Granite models**, and **custom NLP pipelines** to extract clauses, detect missing terms, and flag potential risks, acting as a first-level legal assistant for businesses and individuals.

---

## 🚀 Features

* 📂 **Upload & Parse** – Upload legal contracts and parse them into structured text.
* 📑 **Clause Extraction** – Identify and categorize clauses like confidentiality, liability, termination, etc.
* ✍️ **Plain-Language Summaries** – Convert legal jargon into simple, human-readable summaries.
* 🚦 **Risk Detection** – Flag high-risk or missing clauses using a traffic-light indicator (low/medium/high risk).
* 🔍 **Search & Navigate** – Searchable view of the contract for quick access to key sections.
* 📤 **Export Reports** – Generate reports in PDF/Word format for sharing.

---

## 🛠️ Tech Stack

* **Frontend/UI:** Streamlit
* **Backend/Logic:** Python
* **AI/NLP:**

  * IBM Watson NLU
  * Hugging Face Transformers
  * IBM Granite Models (Speech & NLP)
* **Database:** SQLite (for user authentication & storage)

---

## 📂 Project Structure

```
ClauseWise/
│-- src/
│   │-- core/              # Core document parsing & NLP
│   │-- ui/                # Streamlit app interface
│   │-- database/          # User authentication & storage
│-- requirements.txt       # Python dependencies
│-- README.md              # Project documentation
```

---

## ⚙️ Installation & Setup

1. **Clone the repo**

```bash
git clone https://github.com/Keerthu-08-02/CognitiveX-145-ClauseWiseLegalDocAnalyzer.git
cd CognitiveX-145-ClauseWiseLegalDocAnalyzer
```

2. **Create virtual environment** (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the Streamlit app**

```bash
streamlit run src/ui/streamlit_app.py
```

---

## 🧪 Usage

1. Launch the app in your browser.
2. Upload a contract/legal document (PDF/DOCX).
3. View extracted clauses, summaries, and risk levels.
4. Export a report for team/legal use.

---

## 🎯 Roadmap

* ✅ Basic clause extraction & summarization
* ✅ Risk indicator system
* 🔄 Multi-language legal document support
* 🔄 Real-time speech-to-text legal dictation (Granite ASR)
* 🔄 Collaboration features for legal teams

---

## 🤝 Contributing

Pull requests are welcome! Please follow standard GitHub practices:

* Fork the repo
* Create a feature branch
* Commit changes
* Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** – free to use, modify, and distribute.

---

## 👩‍💻 Author

* **devloper-student** – Developer & Maintainer

## OUTPUT

* https://clausewise-legal-doc-analyzer.streamlit.app/ - use this link for deployd application
