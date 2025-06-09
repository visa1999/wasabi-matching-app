
import streamlit as st

# ================= App Configuration =================
st.set_page_config(page_title="Wasabi Matching App", layout="centered")

# 🌗 Theme Toggle Section
theme = st.radio("🌗 Choose Theme", ["Light", "Dark"], horizontal=True)
if theme == "Dark":
    st.markdown("<style>body{background-color: #0e1117; color: white;}</style>", unsafe_allow_html=True)

# ================= Logo =================
st.image("stacked-logo-full-color-rgb.png", width=220)
st.markdown("<h2 style='text-align: center;'>💼 Wasabi Candidate Matching Assistant</h2>", unsafe_allow_html=True)

# [Your original app logic here remains untouched...]
