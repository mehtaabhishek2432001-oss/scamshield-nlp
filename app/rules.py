import re

MAX_RULE_SCORE = 60

# Each rule: a name, a weight (points added if found), patterns to look for,
# and a plain-English explanation shown to the user.
RULES = [
    {
        "name": "Upfront fee requested",
        "weight": 25,
        "patterns": [
            r"registration\s*(fee|charges?|amount)",
            r"training\s*(fee|charges?)",
            r"security\s*(deposit|fee|amount)",
            r"processing\s*(fee|charges?)",
            r"refundable\s*(deposit|amount|fee)",
            r"kit\s*(fee|charges?)",
            r"(pay|deposit)\s+(rs\.?|₹|inr)\s*\d+",
        ],
        "explanation": "Asks you to pay money. Genuine employers never charge candidates to get a job.",
    },
    {
        "name": "Sensitive personal data requested",
        "weight": 15,
        "patterns": [
            r"aadha+r",
            r"pan\s*card",
            r"(share|send|provide|submit|give)\s.{0,30}bank\s*(account|details|passbook)",
            r"bank\s*(details|passbook)",
            r"\botp\b",
            r"\bcvv\b",
            r"(upi|atm)\s*pin",
        ],
        "explanation": "Mentions Aadhaar, PAN, bank details, OTP, or PINs. Never share these before a verified offer letter.",
    },
    {
        "name": "Guaranteed job or income",
        "weight": 15,
        "patterns": [
            r"guaranteed\s*(job|placement|income|salary|selection)",
            r"100\s*%\s*(job|placement)",
            r"job\s*guarantee",
        ],
        "explanation": "Promises a guaranteed job or income. Real hiring always involves selection.",
    },
    {
        "name": "No interview / instant selection",
        "weight": 12,
        "patterns": [
            r"no\s*interview",
            r"without\s*(any\s*)?interview",
            r"direct\s*(joining|selection)",
            r"instant\s*(joining|selection|offer)",
        ],
        "explanation": "Skips the interview process. Legitimate companies assess candidates before hiring.",
    },
    {
        "name": "Unrealistic earnings",
        "weight": 12,
        "patterns": [
            r"earn\s*(up\s*to\s*)?(rs\.?|₹|inr)\s*[\d,]+\s*(per|/|a)\s*(day|week)",
            r"(daily|weekly)\s*(payment|payout|income)",
            r"earn\s*(money\s*)?(daily|from\s*home)",
            r"work\s*from\s*home.{0,40}earn",
        ],
        "explanation": "Promises easy daily or weekly earnings, a common work-from-home scam pattern.",
    },
    {
        "name": "Personal contact instead of official channel",
        "weight": 10,
        "patterns": [
            r"(contact|message|ping|text|send|reach|call)\s.{0,30}(whats\s*app|telegram)",
            r"(whats\s*app|telegram)\s*(us|me|on|at|no\.?|number|:)",
            r"@(gmail|yahoo|hotmail|outlook|rediffmail)\.com",
            r"(?<![\w#])(\+91[\s-]?)?[6-9]\d{9}(?!\w)",
        ],
        "explanation": "Uses WhatsApp, Telegram, a personal email, or a mobile number instead of an official company channel.",
    },
    {
        "name": "Task-based scam pattern",
        "weight": 10,
        "patterns": [
            r"like\s*(youtube|instagram)\s*(videos?|posts?)",
            r"(rate|review)\s*(products|hotels|apps)",
            r"copy\s*paste\s*(work|job)",
            r"simple\s*(online\s*)?tasks?",
        ],
        "explanation": "Describes 'like videos' or 'rate products' style tasks, often used to lure victims into paying later.",
    },
    {
        "name": "Pressure / urgency tactics",
        "weight": 8,
        "patterns": [
            r"urgent(ly)?\s*(hiring|requirement|opening)",
            r"immediate\s*joining",
            r"limited\s*(seats|slots|vacancies|positions)",
            r"\bhurry\b",
            r"last\s*few\s*(seats|slots)",
        ],
        "explanation": "Creates urgency so you act before thinking or verifying.",
    },
]


def check_rules(text):
    """Check a job post against all scam rules.

    Returns the rule score (0 to 60) and a list of rules that were triggered.
    """
    text = str(text)
    triggered = []
    total = 0

    for rule in RULES:
        for pattern in rule["patterns"]:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                triggered.append({
                    "rule": rule["name"],
                    "weight": rule["weight"],
                    "matched_text": match.group(0),
                    "explanation": rule["explanation"],
                })
                total += rule["weight"]
                break  # count each rule only once

    score = min(total, MAX_RULE_SCORE)

    return {"rule_score": score, "triggered_rules": triggered}
