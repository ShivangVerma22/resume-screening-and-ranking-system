"""
AI Resume Screening & Ranking System
-------------------------------------
No database, no LLM. Uses classical NLP (TF-IDF + Cosine Similarity)
to rank resumes against a job description.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------- Core Functions ----------

def extract_text_from_pdf(file):
    """Extract all text from an uploaded PDF file."""
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return text.strip()


def rank_resumes(job_description, resumes):
    """
    Rank resumes against a job description using TF-IDF + cosine similarity.
    Returns similarity scores scaled 0-100.
    """
    documents = [job_description] + resumes
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(documents).toarray()

    jd_vector = vectors[0]
    resume_vectors = vectors[1:]

    similarities = cosine_similarity([jd_vector], resume_vectors).flatten()
    scores = (similarities * 100).round(2)
    return scores


def get_top_matching_keywords(job_description, resume_text, top_n=5):
    """Find which important JD keywords are present in a resume."""
    vectorizer = TfidfVectorizer(stop_words="english")
    vectorizer.fit([job_description])
    jd_keywords = vectorizer.get_feature_names_out()

    resume_lower = resume_text.lower()
    matched = [kw for kw in jd_keywords if kw in resume_lower]
    return matched[:top_n]


# ---------- Streamlit UI ----------

st.set_page_config(page_title="Resume Screening System", layout="wide")
st.title("Resume Screening & Candidate Ranking System")
st.caption("TF-IDF based matching — no database, no LLM required.")

st.header("1. Job Description")
job_description = st.text_area(
    "Paste the job description here",
    height=180,
    placeholder="e.g. Looking for a Python developer with experience in Machine Learning, FastAPI, and SQL..."
)

st.header("2. Upload Resumes (PDF)")
uploaded_files = st.file_uploader(
    "Upload one or more resumes",
    type=["pdf"],
    accept_multiple_files=True
)

st.divider()

if st.button("Rank Resumes", type="primary"):
    if not job_description.strip():
        st.warning("Please enter a job description first.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        with st.spinner("Processing resumes..."):
            try:
                resume_texts = []
                file_names = []

                for file in uploaded_files:
                    text = extract_text_from_pdf(file)
                    if text:
                        resume_texts.append(text)
                        file_names.append(file.name)
                    else:
                        st.warning(f"Could not extract text from: {file.name} (skipped)")

                if not resume_texts:
                    st.error("No readable text found in the uploaded PDFs.")
                else:
                    scores = rank_resumes(job_description, resume_texts)

                    results = pd.DataFrame({
                        "Resume": file_names,
                        "Match Score (%)": scores
                    }).sort_values(by="Match Score (%)", ascending=False).reset_index(drop=True)

                    results.index += 1  # start ranking from 1

                    st.header("3. Ranking Results")
                    st.dataframe(results, use_container_width=True)

                    # Show top matching keywords per resume
                    st.header("4. Matched Keywords (per resume)")
                    for name, text in zip(file_names, resume_texts):
                        keywords = get_top_matching_keywords(job_description, text)
                        with st.expander(f"{name}"):
                            if keywords:
                                st.write(", ".join(keywords))
                            else:
                                st.write("No strong keyword overlap found.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
