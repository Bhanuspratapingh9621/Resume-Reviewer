# Smart Resume Reviewer — Streamlit MVP
# -------------------------------------------------------------
# Author: Bhanu Pratap Singh
# Run:  streamlit run app.py
# Python: 3.10+
# -------------------------------------------------------------

import os
import io
import json
import re
from typing import List, Dict, Any

import streamlit as st

# PDF parsing
try:
    import fitz  # PyMuPDF
except Exception as e:
    fitz = None

# LLM SDK
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# Optional: .env support
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# -----------------------------
# NEW & IMPROVED CUSTOM STYLING (CSS)
# -----------------------------

    
    # (This function is inside your app.py)
def apply_custom_styling():
    st.markdown("""
    <style>
        /* --- NEW, MORE RELIABLE STYLING --- */

        /* General body styling */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Reduce top padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* --- Sidebar Styling (FIXED) --- */
        .stSidebar {
            background-color: #0F172A; /* Deeper navy blue */
        }
        /* Set a default light color for all text elements in the sidebar */
        .stSidebar, .stSidebar *, .stSidebar p, .stSidebar li, .stSidebar div, .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar label {
            color: #E2E8F0 !important; /* Light grey text for readability */
        }
        /* Make headers fully white for emphasis */
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: #FFFFFF !important;
        }
        /* Style the info box */
        .stSidebar [data-testid="stAlert"] {
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        /* --- Main Content Styling --- */
        [data-testid="stHorizontalBlock"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        h2 {
            color: #1E2A38;
            font-weight: 600;
            border-bottom: 2px solid #F1F5F9;
            padding-bottom: 8px;
        }

        /* --- Button Styling --- */
        .stButton>button {
            border: none;
            background: linear-gradient(90deg, #4F46E5, #818CF8);
            color: white !important; /* Important to override default */
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            box-shadow: 0 0 15px rgba(79, 70, 229, 0.5);
            transform: scale(1.02);
            color: white !important;
        }
        
        /* --- Footer Styling --- */
        footer { visibility: hidden; }
        .footer-custom {
            text-align: center;
            padding: 1rem;
            color: #64748B;
        }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# Helpers & Prompts (No Changes Here)
# -----------------------------
def read_pdf_bytes_to_text(pdf_bytes: bytes) -> str:
    if fitz is None: raise RuntimeError("PyMuPDF (fitz) not installed. Please `pip install pymupdf`. ")
    text_chunks: List[str] = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc: text_chunks.append(page.get_text("text"))
    text = "\n".join(text_chunks)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text

def get_client() -> Any:
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    if not api_key: raise RuntimeError("OPENAI_API_KEY missing. For local use, create a .env file. For deployment, add it to Streamlit secrets.")
    if OpenAI is None: raise RuntimeError("openai SDK not installed. Please `pip install openai`. ")
    return OpenAI(api_key=api_key)

def call_llm(system: str, user: str, json_mode: bool = True, model: str = "gpt-4o-mini") -> str:
    client = get_client()
    kwargs = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "temperature": 0.2}
    if json_mode: kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content

SCORING_RUBRIC = {"keyword_match": "Measures how well resume covers skills / keywords from target JD.", "impact_and_metrics": "Use of numbers (%, $, time) and outcomes.", "clarity_and_structure": "Readable sections, bullet quality, no fluff.", "relevance": "Content aligned with target role and domain.", "language_and_tone": "Concise, professional, action verbs, tense consistency."}
STRUCTURED_JSON_SPEC = {"type": "object", "properties": {"scores": {"type": "object", "properties": {k: {"type": "integer"} for k in SCORING_RUBRIC.keys()}, "required": list(SCORING_RUBRIC.keys())}, "top_missing_keywords": {"type": "array", "items": {"type": "string"}}, "section_feedback": {"type": "object", "properties": {"summary": {"type": "string"}, "experience": {"type": "string"}, "projects": {"type": "string"}, "skills": {"type": "string"}, "education": {"type": "string"}}}, "bullet_suggestions": {"type": "array", "items": {"type": "object", "properties": {"original": {"type": "string"}, "improved": {"type": "string"}}}}, "final_resume_markdown": {"type": "string"}}, "required": ["scores", "top_missing_keywords", "section_feedback", "final_resume_markdown"]}
SYSTEM_PROMPT = ("You are an ATS-savvy resume coach. Be concise, specific, and data-driven. Always prefer bullet points with metrics (%, $, time saved, throughput). Follow Indian fresher/early-career norms when appropriate (1 page, clear sections).")
USER_PROMPT_TMPL = ("You will review a resume against a target job role and optional job description.\n\nReturn STRICT JSON that validates this JSON Schema: {schema}.\n\nScoring: 1 (poor) to 10 (excellent).\n\nInput:\nTARGET ROLE: {role}\n\nJOB DESCRIPTION (optional):\n{jd}\n\nRESUME TEXT:\n{resume}\n\nInstructions:\n1) Fill 'scores' for keyword_match, impact_and_metrics, clarity_and_structure, relevance, language_and_tone.\n2) 'top_missing_keywords': 8-15 ATS keywords missing or weak.\n3) 'section_feedback': crisp suggestions per section.\n4) 'bullet_suggestions': rewrite 4-8 weakest bullets using STAR and metrics.\n5) 'final_resume_markdown': produce a role-tailored resume in clean Markdown with sections: SUMMARY, SKILLS, EXPERIENCE, PROJECTS, EDUCATION, CERTIFICATIONS (if any). Use impactful, quantified bullets.\n")

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="AI Resume Reviewer", page_icon="✨", layout="wide")

# Apply the new custom CSS
apply_custom_styling()

# --- HEADER ---
st.title("✨ AI Resume Reviewer")
st.markdown("Get instant, AI-powered feedback to make your resume stand out. Let's land your dream job!")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    st.info("💡 **Pro-Tip**:\n`gpt-4o` is smarter but slower. `gpt-4o-mini` is much faster for quick checks!")
    st.markdown("---")
    st.markdown("Created with ❤️ by **Bhanu Pratap Singh**.")

# --- MAIN CONTENT ---
with st.container():
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📄Upload Your Resume")
        pdf_file = st.file_uploader("Upload resume (PDF)", type=["pdf"], label_visibility="collapsed")
        resume_text = ""
        if pdf_file is not None:
            try:
                resume_text = read_pdf_bytes_to_text(pdf_file.getvalue())
                st.success(f"✅ Parsed your resume.")
            except Exception as e:
                st.error(f"❌ PDF parsing failed: {e}")
        st.markdown("**OR** paste resume text:")
        resume_text_manual = st.text_area("Resume Text", height=220, placeholder="Paste your resume text here,if you don't have pdf.", label_visibility="collapsed")
        if not resume_text and resume_text_manual:
            resume_text = resume_text_manual

    with col_right:
        st.subheader("🎯Your Target Job")
        target_role = st.text_input("Target Role", placeholder="E.g.- Software Engineer,", label_visibility="collapsed")
        jd_text = st.text_area("Job Description (Recommended)", height=287, placeholder="Enter the complete job description for the target role.")

st.markdown("---")

analyze = st.button("🚀 Analyze My Resume!", type="primary", use_container_width=True, disabled=not bool(resume_text.strip()))

if analyze:
    # (Analysis logic remains the same)
    with st.spinner("Thinking like an ATS + Hiring Manager..."):
        try:
            user_prompt = USER_PROMPT_TMPL.format(schema=json.dumps(STRUCTURED_JSON_SPEC), role=target_role.strip() or "Unknown", jd=jd_text.strip() or "(none)", resume=resume_text.strip()[:12000])
            raw = call_llm(SYSTEM_PROMPT, user_prompt, json_mode=True, model=model)
            try: data = json.loads(raw)
            except Exception:
                m = re.search(r"\{.*\}\s*$", raw, flags=re.DOTALL)
                if m: data = json.loads(m.group(0))
                else: raise ValueError("Model did not return valid JSON. Raw output:\n" + raw)
        except Exception as e:
            st.error(f"LLM call failed: {e}")
            data = None

    if data:
        st.success("Review complete ✅")
        st.subheader("📊 Your Scores (out of 10)")
        scores = data.get("scores", {})
        if scores:
            cols = st.columns(len(scores))
            for i, (k, v) in enumerate(scores.items()):
                with cols[i]: st.metric(k.replace("_", " ").title(), v)

        tab1, tab2, tab3, tab4 = st.tabs(["📄 Tailored Resume", "🔎 Missing Keywords", "✍️ Bullet Improvements", "🧩 Section Feedback"])

        with tab1:
            final_md = data.get("final_resume_markdown", "")
            st.markdown(final_md)
            st.download_button("⬇️ Download Resume (.md)", final_md.encode("utf-8"), f"resume_{target_role.replace(' ','_').lower()}.md", "text/markdown")

        with tab2:
            missing = data.get("top_missing_keywords", [])
            if missing: st.info(", ".join(f"`{keyword}`" for keyword in missing))
            else: st.write("(None detected)")

        with tab3:
            bullets = data.get("bullet_suggestions", [])
            if bullets:
                for item in bullets:
                    st.markdown(f"- **Original:** {item.get('original','')}\n- **Improved:** {item.get('improved','')}")
            else: st.write("(No bullet suggestions returned)")

        with tab4:
            sec = data.get("section_feedback", {})
            for section_name in ["summary", "experience", "projects", "skills", "education"]:
                if section_name in sec and sec[section_name]:
                    with st.expander(section_name.title()): st.write(sec[section_name])

# --- FOOTER ---
st.markdown("<div class='footer-custom'>Built with Streamlit + OpenAI by Bhanu Pratap Singh ❤️</div>", unsafe_allow_html=True)