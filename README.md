# 🛡️ ScamShield: Fake Job & Internship Post Detector

ScamShield estimates how risky a job or internship post is by combining a **machine learning model** with **India-specific scam rules**, then explains *why* in plain language.

**Live demo:** _coming soon_

## The problem

Fake job and internship posts trick students and job seekers into paying "registration fees", sharing Aadhaar or bank details, or doing unpaid "tasks". Many scams look professional enough to fool people at a glance.

## How it works

ScamShield uses a hybrid approach, because each part covers what the other misses:

| Component | What it does | Max score |
|---|---|---|
| **ML model** (TF-IDF + Logistic Regression) | Learns language patterns from ~15,900 real and fake job posts | 40 |
| **Rule engine** (8 weighted regex rules) | Catches India-specific red flags: registration fees, Aadhaar/OTP requests, WhatsApp contact, "no interview", unrealistic daily earnings | 60 |

**Final score** = the higher of (rule score + ML probability × 40) or (ML probability × 100), capped at 100.

| Score | Label |
|---|---|
| 70–100 | 🚨 HIGH RISK |
| 40–69 | ⚠️ MEDIUM RISK |
| 0–39 | ✅ LOW RISK |

Every result lists the exact phrases that triggered each rule, plus practical safety advice.

## Results

Evaluated on a held-out test set of 3,176 posts (3,033 real, 143 fake):

| Metric | Score |
|---|---|
| Recall (scams caught) | **82.5%** |
| Precision | 59.9% |
| F1-score | 0.694 |
| ROC-AUC | 0.964 |
| Accuracy | 96.7% |

Only ~4.5% of posts are fake, so a model that always predicts "real" would already score ~95% accuracy. That's why this project optimizes for **recall** and **F1**, not accuracy.

## Key findings

- **Removed 2,001 duplicate posts** before training so test scores aren't inflated by memorized copies. Fake posts were duplicated more often than real ones (17.7% vs 10.9%).
- **Found and fixed a rule bug using data:** the phone-number rule was matching anonymized hash codes in the dataset, flagging 305 genuine posts. Tightening the patterns cut false alarms on real posts by ~78%.
- **Redesigned the scoring formula after testing:** the original "rules + ML × 40" formula labeled a scam the model was 96% sure about as LOW RISK. Letting a confident ML score stand on its own fixed this.
- **Known model limitations:** the dataset is mostly US posts from 2012–2014, and stop-word removal drops negations (e.g., "no interview" becomes "interview"). The rule engine covers both gaps.

## Tech stack

Python · pandas · scikit-learn · Streamlit · joblib · Jupyter

## Project structure

```
scamshield/
├── app/
│   ├── main.py           # Streamlit web app
│   ├── risk_engine.py    # Combines ML + rules into a final risk score
│   ├── rules.py          # India-specific scam rules
│   └── train_model.py    # Trains and saves the model
├── models/
│   ├── scamshield_model.pkl
│   └── metrics.json
├── notebooks/
│   ├── explore_dataset.ipynb
│   ├── clean_dataset.ipynb
│   └── test_scamshield.ipynb
└── requirements.txt
```

## Run locally (Windows)

```cmd
git clone https://github.com/YOUR-USERNAME/scamshield-nlp.git
cd scamshield-nlp
py -3.11 -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
streamlit run app/main.py
```

To retrain the model, download the [Real or Fake Job Posting Prediction](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction) dataset from Kaggle, save it as `data/fake_job_postings.csv`, run `notebooks/clean_dataset.ipynb`, then run `python app/train_model.py`.

## Disclaimer

ScamShield is an educational risk-assessment tool, not a legal verdict. A low score does not guarantee a job is genuine, and a high score does not prove fraud. To report fraud in India, visit [cybercrime.gov.in](https://cybercrime.gov.in) or call **1930**.