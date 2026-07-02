import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import json
import re
from datetime import datetime
import base64
import time
import matplotlib.pyplot as plt
import pickle

# ================== CONFIG ==================
GOOGLE_API_KEY = "AIzaSyB7BPPwVTOUbtM8tNklcP5qbxTOCBHsc4k"
genai.configure(api_key=GOOGLE_API_KEY)

# ================== GEMINI ==================
def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-3-flash-preview')
    with st.spinner("Analyzing..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
            progress_bar.progress(i + 1)
        response = model.generate_content(input_text)
    return response.text

# ================== PDF READER ==================
def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

# ================== SAFE PARSER ==================
def convert_to_float(value):
    """Convert AI string values safely to float"""
    try:
        value = str(value).strip()

        if value.endswith('%'):
            return float(value.rstrip('%'))

        elif '/' in value:  # e.g. 4/10
            num, denom = value.split('/')
            return (float(num) / float(denom)) * 100

        else:
            return float(value)

    except:
        return 0.0


def parse_ai_response(response):
    response = response.strip()

    match = re.search(r'\{.*\}', response, re.DOTALL)
    if not match:
        st.error("No valid JSON found")
        return None

    try:
        parsed = json.loads(match.group())

        keys = ['JD Match', 'TechnicalSkills', 'SoftSkills', 'Experience', 'Education', 'Projects']

        for key in keys:
            if key in parsed:
                parsed[key] = convert_to_float(parsed[key])

        return parsed

    except Exception as e:
        st.error(f"Parsing error: {str(e)}")
        return None

# ================== UTIL ==================
def get_download_link(text):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="history.txt">Download History</a>'

# ================== SUGGESTIONS ==================
def suggest_improvements(missing_keywords, job_description):
    prompt = f"""
    Suggest how to add these keywords into resume:
    {missing_keywords}

    Job Description:
    {job_description}
    """
    return get_gemini_response(prompt)

# ================== CHART ==================
def create_radar_chart(parsed):
    categories = ['TechnicalSkills', 'SoftSkills', 'Experience', 'Education', 'Projects']
    scores = [parsed.get(cat, 0) for cat in categories]

    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    ax.plot(categories, scores)
    ax.fill(categories, scores, alpha=0.2)
    return fig

# ================== STORAGE ==================
def save_analysis(data):
    with open("analysis.pkl", "wb") as f:
        pickle.dump(data, f)


def load_analysis():
    if os.path.exists("analysis.pkl"):
        with open("analysis.pkl", "rb") as f:
            return pickle.load(f)
    return []

# ================== PROMPT ==================
input_prompt = """
Act like an ATS system.

Return ONLY valid JSON:
{{
"JD Match": "percentage (0-100)",
"MissingKeywords": [],
"Profile Summary": "",
"TechnicalSkills": "percentage (0-100)",
"SoftSkills": "percentage (0-100)",
"Experience": "percentage (0-100)",
"Education": "percentage (0-100)",
"Projects": "percentage (0-100)"
}}

resume: {text}
description: {jd}
"""

# ================== UI ==================
st.set_page_config(page_title="SmartResume Analyzer")
st.title("Smart Resume Analyzer")

if 'history' not in st.session_state:
    st.session_state.history = load_analysis()

jd = st.text_area("Paste Job Description")
file = st.file_uploader("Upload Resume (PDF)")

if st.button("Submit"):
    if not file:
        st.warning("Upload resume")

    else:
        text = input_pdf_text(file)

        if text:
            response = get_gemini_response(input_prompt.format(text=text, jd=jd))
            parsed = parse_ai_response(response)

            if parsed:
                st.metric("JD Match", f"{parsed['JD Match']:.1f}%")

                st.subheader("Missing Keywords")
                st.write(parsed.get("MissingKeywords", []))

                st.subheader("Summary")
                st.write(parsed.get("Profile Summary", ""))

                st.subheader("Suggestions")
                if parsed.get("MissingKeywords"):
                    st.write(suggest_improvements(parsed["MissingKeywords"], jd))

                st.subheader("Analysis Chart")
                st.pyplot(create_radar_chart(parsed))

                st.session_state.history.append({
                    "date": str(datetime.now()),
                    "match": parsed['JD Match'],
                    "keywords": parsed.get("MissingKeywords", [])
                })

# ================== SIDEBAR ==================
st.sidebar.title("History")

for item in st.session_state.history:
    st.sidebar.write(item)

if st.sidebar.button("Save"):
    save_analysis(st.session_state.history)

if st.sidebar.button("Download History"):
    text = json.dumps(st.session_state.history, indent=2)
    st.sidebar.markdown(get_download_link(text), unsafe_allow_html=True)
