
import streamlit as st
import pandas as pd
import re
import docx2txt
from PyPDF2 import PdfReader
import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Wasabi Candidate App", layout="centered")

# ---------------- THEME TOGGLE ----------------
theme = st.radio("🌗 Choose Theme", ["Light", "Dark"], horizontal=True)
if theme == "Dark":
    st.markdown("""
        <style>
        html, body, .main {
            background-color: #0e1117 !important;
            color: white !important;
        }
        textarea, input, .stTextInput > div > div > input,
        .stTextArea textarea, .stSelectbox div[data-baseweb="select"],
        .stFileUploader, .stDownloadButton button, .stButton button,
        .stRadio, .stCheckbox, .stSelectbox {
            background-color: #1e222a !important;
            color: white !important;
            border: 1px solid #3a3f47 !important;
        }
        .stDataFrame {
            background-color: #1e1e1e !important;
            color: white !important;
        }
        .css-1d391kg, .css-1cpxqw2 {
            background-color: #0e1117 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------- LOGO ----------------
st.image("stacked-logo-full-color-rgb.png", width=200)
st.markdown("<h2 style='text-align: center;'>💼 Wasabi Candidate Matching Assistant</h2>", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "job_title" not in st.session_state: st.session_state["job_title"] = ""
if "keywords" not in st.session_state: st.session_state["keywords"] = []
if "match_results" not in st.session_state: st.session_state["match_results"] = []
if "hiring_view" not in st.session_state: st.session_state["hiring_view"] = False
if "history" not in st.session_state: st.session_state["history"] = []

# ---------------- HELPERS ----------------
def extract_text_from_pdf(file): return " ".join([p.extract_text() or "" for p in PdfReader(file).pages])

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

# ---------------- JD SECTION ----------------
st.markdown("### 📄 Paste Job Description")
jd_text = st.text_area("Paste full JD text here", height=200)
if st.button("🔍 Extract Job Title & Keywords"):
    if jd_text.strip():
        title, keywords = extract_keywords_and_title(jd_text)
        st.session_state["job_title"] = title
        st.session_state["keywords"] = keywords
        st.success("✅ JD analyzed!")
        st.markdown(f"**🧑‍💼 Job Title:** `{title}`")
        st.markdown(f"**🧠 Keywords:** `{', '.join(keywords)}`")

# ---------------- RESUME UPLOAD ----------------
st.markdown("### 📤 Upload Resume(s)")
uploaded_files = st.file_uploader("Upload .pdf or .docx resumes", type=["pdf", "docx"], accept_multiple_files=True)

# ---------------- LINKEDIN TEXT ----------------
st.markdown("### 🔗 Paste LinkedIn Profile Text")
linkedin_text = st.text_area("Paste LinkedIn summary or full profile text here", height=200)

# ---------------- MATCHING ----------------
if st.button("📊 Compare & Generate Scoreboard"):
    results = []
    keywords = st.session_state["keywords"]
    job_title = st.session_state["job_title"]

    if uploaded_files:
        for file in uploaded_files:
            name = file.name.replace(".pdf", "").replace(".docx", "")
            text = extract_text_from_pdf(file) if file.name.endswith(".pdf") else docx2txt.process(file)
            score, matched, missing = match_resume_to_jd(text, keywords)
            inmail = f"Hi {name}, your experience with {', '.join(matched)} aligns well with our {job_title} role. Let’s connect!"
            results.append({
                "Candidate": name,
                "Score": f"{score}%",
                "Matched Skills": ", ".join(matched),
                "Missing Skills": ", ".join(missing),
                "InMail": inmail,
                "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })

    if linkedin_text.strip():
        score, matched, missing = match_resume_to_jd(linkedin_text, keywords)
        inmail = f"Hi, your LinkedIn profile shows great alignment with our {job_title} role, especially in {', '.join(matched)}."
        results.append({
            "Candidate": "LinkedIn Paste",
            "Score": f"{score}%",
            "Matched Skills": ", ".join(matched),
            "Missing Skills": ", ".join(missing),
            "InMail": inmail,
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    if results:
        df = pd.DataFrame(results)
        st.session_state["match_results"] = df
        st.session_state["history"].extend(results)
        st.success("✅ Scoreboard generated!")
        st.dataframe(df[["Candidate", "Score", "Matched Skills", "Missing Skills"]])
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), "match_results.csv")
        st.markdown("### ✉️ InMail Generator")
        selected = st.selectbox("Select candidate", df["Candidate"])
        msg = df[df["Candidate"] == selected]["InMail"].values[0]
        st.text_area("InMail Message", msg, height=150)
    else:
        st.warning("⚠️ No data to compare.")

# ---------------- HIRING MANAGER ----------------
st.markdown("---")
if st.checkbox("🔒 View as Hiring Manager"):
    password = st.text_input("Enter hiring manager password:", type="password")
    if password == "wasabiadmin":
        st.session_state["hiring_view"] = True
    else:
        st.warning("Incorrect password.")

if st.session_state["hiring_view"]:
    st.markdown("## 📁 Hiring Manager Dashboard")
    if st.session_state["history"]:
        hist_df = pd.DataFrame(st.session_state["history"])
        st.dataframe(hist_df)
        st.download_button("⬇️ Export Full History", hist_df.to_csv(index=False), "full_history.csv")
    else:
        st.info("No matching history available yet.")
