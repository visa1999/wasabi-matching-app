
import streamlit as st
import pandas as pd
import re
import docx2txt
from PyPDF2 import PdfReader

# ----------------- CONFIG -----------------
st.set_page_config(page_title="Wasabi Matching Assistant", layout="centered")

# ----------------- HEADER WITH LOCAL LOGO -----------------
st.image("stacked-logo-full-color-rgb.png", width=200)
st.markdown("## 💼 Wasabi Candidate Matching Assistant")
st.markdown("Upload a JD, resume, or LinkedIn content to compare candidate fit.")

# ----------------- FUNCTIONS -----------------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return " ".join([page.extract_text() or "" for page in reader.pages])

def extract_keywords_and_title(jd_text):
    lines = jd_text.strip().split("\n")
    first_line = next((line for line in lines if line.strip()), "")
    title_match = re.search(r"(Job Title|Position):\s*(.+)", jd_text, re.IGNORECASE)
    job_title = title_match.group(2).strip() if title_match else first_line
    skills = [
        "Python", "Go", "Java", "Rust", "C++", "C#", "Golang", "TypeScript", "React", "Angular", "Node.js",
        "Flask", "Django", "Spring", "Express", "AWS", "GCP", "Azure", "Cloud", "CI/CD", "DevOps", "Docker",
        "Kubernetes", "Terraform", "Ansible", "Linux", "Jenkins", "Bash", "Shell", "SQL", "NoSQL",
        "PostgreSQL", "MongoDB", "Snowflake", "ETL", "Airflow", "GraphQL", "REST API", "SOAP",
        "Microservices", "Big Data", "Machine Learning", "NLP", "LLM", "Pandas", "NumPy", "Spark"
    ]
    found = [kw for kw in skills if re.search(rf'\b{re.escape(kw)}\b', jd_text, re.IGNORECASE)]
    return job_title, sorted(list(set(found)))

def match_resume_to_jd(text, jd_keywords):
    matched = [kw for kw in jd_keywords if kw.lower() in text.lower()]
    missing = [kw for kw in jd_keywords if kw.lower() not in text.lower()]
    score = round((len(matched) / len(jd_keywords)) * 100, 1) if jd_keywords else 0
    return score, matched, missing

# ----------------- SESSION STATE -----------------
if "job_title" not in st.session_state:
    st.session_state["job_title"] = ""
if "keywords" not in st.session_state:
    st.session_state["keywords"] = []
if "match_results" not in st.session_state:
    st.session_state["match_results"] = None

# ----------------- JD SECTION -----------------
st.markdown("### 📄 Paste Job Description")
jd_text = st.text_area("Paste JD text here", height=200)
if st.button("🔍 Generate JD Keywords & Job Title"):
    if jd_text.strip():
        title, keywords = extract_keywords_and_title(jd_text)
        st.session_state["job_title"] = title
        st.session_state["keywords"] = keywords
        st.success("JD analyzed!")
        st.markdown(f"**📌 Job Title:** `{title}`")
        st.markdown(f"**🧠 Keywords:** `{', '.join(keywords)}`")

# ----------------- RESUME UPLOAD SECTION -----------------
st.markdown("### 📥 Upload Resume")
uploaded_files = st.file_uploader("Upload resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# ----------------- LINKEDIN TEXT SECTION -----------------
st.markdown("### 🔗 Paste LinkedIn Profile Content")
linkedin_text = st.text_area("Paste LinkedIn summary or experience section")

# ----------------- COMPARISON LOGIC -----------------
if st.button("📊 Generate Scoreboard & InMail"):
    results = []
    if uploaded_files:
        for file in uploaded_files:
            name = file.name.replace(".pdf", "").replace(".docx", "")
            text = extract_text_from_pdf(file) if file.name.endswith(".pdf") else docx2txt.process(file)
            score, matched, missing = match_resume_to_jd(text, st.session_state["keywords"])
            inmail = f"Hi {name}, your experience with {', '.join(matched)} aligns well with our {st.session_state['job_title']} role. Let’s connect!"
            results.append({
                "Candidate": name,
                "Score": f"{score}%",
                "Matched Skills": ", ".join(matched),
                "Missing Skills": ", ".join(missing),
                "InMail": inmail
            })

    if linkedin_text.strip():
        score, matched, missing = match_resume_to_jd(linkedin_text, st.session_state["keywords"])
        inmail = f"Hi, your LinkedIn profile shows great alignment with our {st.session_state['job_title']} role, especially in {', '.join(matched)}."
        results.append({
            "Candidate": "LinkedIn Paste",
            "Score": f"{score}%",
            "Matched Skills": ", ".join(matched),
            "Missing Skills": ", ".join(missing),
            "InMail": inmail
        })

    if results:
        df = pd.DataFrame(results)
        st.session_state["match_results"] = df
        st.dataframe(df[["Candidate", "Score", "Matched Skills", "Missing Skills"]])
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), "match_results.csv")

        st.markdown("### ✉️ InMail Generator")
        selected = st.selectbox("Select candidate", df["Candidate"])
        msg = df[df["Candidate"] == selected]["InMail"].values[0]
        st.text_area("InMail Message", msg, height=150)
    else:
        st.warning("⚠️ No data found to compare.")
