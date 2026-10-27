import sys
from pathlib import Path

import streamlit as st

# Make sure Python can find risk_engine.py and rules.py in this folder
sys.path.append(str(Path(__file__).resolve().parent))

from risk_engine import analyze_job_post, load_model

st.set_page_config(page_title="ScamShield", page_icon="🛡️", layout="centered")


@st.cache_resource
def get_model():
    """Load the model once and reuse it for every analysis."""
    return load_model()


model = get_model()

# ---------- Header ----------
st.title("🛡️ ScamShield")
st.subheader("Fake Job & Internship Post Detector")
st.write(
    "Paste a job or internship post below. ScamShield combines a machine learning "
    "model with India-specific scam rules to estimate how risky the post is."
)

# ---------- Input ----------
job_text = st.text_area(
    "Job post",
    height=250,
    placeholder="Paste the full job or internship post here...",
)

# ---------- Analysis ----------
if st.button("Analyze Job Post", type="primary"):
    if not job_text.strip():
        st.warning("Please paste a job post first.")
    else:
        result = analyze_job_post(job_text, model)
        score = result["risk_score"]
        label = result["risk_label"]

        st.divider()

        if label == "HIGH RISK":
            st.error(f"### 🚨 {label}: {score} / 100")
        elif label == "MEDIUM RISK":
            st.warning(f"### ⚠️ {label}: {score} / 100")
        else:
            st.success(f"### ✅ {label}: {score} / 100")

        st.progress(score)

        col1, col2, col3 = st.columns(3)
        col1.metric("Final risk score", f"{score} / 100")
        col2.metric("ML scam probability", f"{result['ml_probability']:.0%}")
        col3.metric("Rule score", f"{result['rule_score']} / 60")

        st.markdown("#### 🔍 Why this result")
        for e in result["explanations"]:
            st.markdown("- " + e.replace("$", "\\$"))

        st.markdown("#### 🛡️ Safety advice")
        for a in result["safety_advice"]:
            st.markdown("- " + a)

# ---------- Disclaimer ----------
st.divider()
st.caption(
    "⚠️ Disclaimer: ScamShield is an educational risk-assessment tool, not a legal verdict. "
    "A low score does not guarantee a job is genuine, and a high score does not prove fraud. "
    "Always verify employers independently. To report fraud in India, visit cybercrime.gov.in or call 1930."
)
