# 📄 AI Resume Analyzer ATS

An intelligent Applicant Tracking System (ATS) simulator designed to help job seekers optimize their resumes for modern automated recruitment pipelines. Powered by Python, Streamlit, and Google's Gemini LLM.

## ✨ Key Features
* 🔍 **ATS Scoring:** Instantly calculates the matching percentage (0-100%) between your resume (PDF) and a job description.
* 🎯 **Missing Keyword Analysis:** Identifies critical skills and keywords missing from your resume.
* 📊 **Interactive Radar Chart:** Visualizes your profile strength across Technical Skills, Soft Skills, Experience, Education, and Projects.
* 💡 **Tailored AI Suggestions:** Provides actionable, step-by-step guidance on how to integrate missing keywords naturally into your CV.
* 💾 **History Management:** Locally saves your resume analysis history with option to download as a text file.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **AI Model:** Google Gemini (Generative AI)
* **Libraries:** PyPDF2 (PDF Parsing), Matplotlib (Radar charts), Python Pickle (History Storage)

## 🚀 Setup & Installation

1. Install the required dependencies:
   ```bash
   pip install google-generativeai PyPDF2 streamlit matplotlib
   ```

2. Run the application:
   ```bash
   streamlit run adv_ats_new.py
   ```

