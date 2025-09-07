# ✨ AI Resume Reviewer

**AI Resume Reviewer** is a powerful web application built with **Streamlit** and powered by **Large Language Models (LLMs)** to help job seekers **optimize their resumes**.  
It compares your resume against a specific job description and provides:

✅ Instant, actionable feedback  
✅ Tailored suggestions  
✅ A rewritten resume optimized for **ATS** and recruiters  

---

## 🚀 Key Features

- **📤 Dual Upload Options**  
  Upload your resume as a **PDF** or **paste text** directly.

- **🎯 Targeted Analysis**  
  Get feedback aligned with your target **job title** and **description**.

- **🤖 Comprehensive AI Review**
  - **Keyword Matching** – Detect missing keywords from the job description.  
  - **Impact & Metrics** – Suggest quantifiable improvements (%, $, numbers).  
  - **Clarity & Structure** – Improve readability and professional tone.

- **📊 Resume Scoring**  
  Get a **quantitative score** on ATS compatibility and overall strength.

- **🧩 Structured Feedback Tabs**
  - **Tailored Resume** – AI-generated, improved resume in Markdown.
  - **Missing Keywords** – Essential keywords to include.
  - **Bullet Improvements** – Before vs After suggestions.
  - **Section Feedback** – Specific recommendations for each section.

- **📥 Downloadable Reports**  
  Export:
  - Optimized Resume (**.pdf**)  
  - Full Feedback Report (**.txt**)  

---

## 🛠 Tech Stack
- **Framework:** Streamlit  
- **Language:** Python  
- **AI/LLM:** OpenAI (GPT-4o / GPT-4o-mini)  
- **PDF Parsing:** PyMuPDF  
- **Dependencies:** `requirements.txt`  

---

## ⚙️ Setup & Local Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
2️⃣ Install Dependencies


pip install -r requirements.txt
3️⃣ Set Up Your API Key
Create a folder named .streamlit in the root directory.

Inside .streamlit, create a file secrets.toml and add:



OPENAI_API_KEY = "sk-your-secret-api-key"
4️⃣ Run the Application




streamlit run app.py



✨ Contributions are welcome!
⭐ If you like this project, give it a star on GitHub!


---

### ✅ ** requirements.txt**
Here’s what you need:



