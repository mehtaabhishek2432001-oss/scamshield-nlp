from pathlib import Path

import joblib

# Works both when imported as "app.risk_engine" (notebooks)
# and as "risk_engine" (Streamlit app inside the app folder).
try:
    from .rules import check_rules
except ImportError:
    from rules import check_rules

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "scamshield_model.pkl"

ML_MAX_SCORE = 40
HIGH_THRESHOLD = 70
MEDIUM_THRESHOLD = 40

SAFETY_ADVICE = {
    "HIGH RISK": [
        "Do NOT pay any registration, training, or security fee.",
        "Do NOT share Aadhaar, PAN, bank details, OTP, or UPI PIN.",
        "Verify the company on its official website and LinkedIn page.",
        "Report suspected fraud at cybercrime.gov.in or call the 1930 helpline.",
    ],
    "MEDIUM RISK": [
        "Verify the company independently before sharing any personal details.",
        "Ask for communication from an official company email domain.",
        "Search the company name with words like 'scam' or 'fraud' for reviews.",
        "Never pay money to get a job, even if it is called 'refundable'.",
    ],
    "LOW RISK": [
        "No strong scam signals found, but always verify the employer.",
        "Apply through the company's official careers page where possible.",
        "Never pay any fee to get a job.",
    ],
}


def load_model(path=MODEL_PATH):
    """Load the trained TF-IDF + Logistic Regression pipeline."""
    return joblib.load(path)


def get_risk_label(score, high=HIGH_THRESHOLD, medium=MEDIUM_THRESHOLD):
    if score >= high:
        return "HIGH RISK"
    if score >= medium:
        return "MEDIUM RISK"
    return "LOW RISK"


def analyze_job_post(text, model, high=HIGH_THRESHOLD, medium=MEDIUM_THRESHOLD):
    """Combine the ML probability and rule score into one risk assessment."""
    text = str(text)
    if not text.strip():
        raise ValueError("Job post text is empty.")

    # 1. Machine learning part (max 40 points)
    ml_probability = float(model.predict_proba([text])[0][1])
    ml_score = ml_probability * ML_MAX_SCORE

    # 2. Rule-based part (max 60 points)
    rule_result = check_rules(text)
    rule_score = rule_result["rule_score"]
    triggered_rules = rule_result["triggered_rules"]

    # 3. Final score (max 100)
    # Take the higher of: rules + ML (original formula) or ML alone on a 0-100 scale,
    # so a confident ML detection is not hidden when no rules fire.
    combined_score = rule_score + ml_score
    ml_only_score = ml_probability * 100
    risk_score = min(round(max(combined_score, ml_only_score)), 100)
    risk_label = get_risk_label(risk_score, high, medium)

    # 4. Explanations
    explanations = []
    for r in triggered_rules:
        explanations.append(f"{r['rule']} (found: \"{r['matched_text']}\"): {r['explanation']}")

    if ml_probability >= 0.7:
        explanations.append(
            f"The ML model finds this post's language strongly similar to known fake job posts ({ml_probability:.0%})."
        )
    elif ml_probability >= 0.4:
        explanations.append(
            f"The ML model finds this post's language somewhat similar to known fake job posts ({ml_probability:.0%})."
        )
    else:
        explanations.append(
            f"The ML model finds this post's language closer to genuine job posts ({ml_probability:.0%} scam probability)."
        )

    return {
        "risk_score": risk_score,
        "risk_label": risk_label,
        "ml_probability": round(ml_probability, 4),
        "ml_score": round(ml_score, 1),
        "rule_score": rule_score,
        "triggered_rules": triggered_rules,
        "explanations": explanations,
        "safety_advice": SAFETY_ADVICE[risk_label],
    }