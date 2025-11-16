import pandas as pd
from datetime import datetime
import os

LOG_PATH = "data/logs.csv"

def log_event(input_text, safety_result):
    os.makedirs("data", exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "input_text": input_text,
        "is_harmful": safety_result.get("is_harmful"),
        "category": safety_result.get("category"),
        "explanation": safety_result.get("explanation")
    }

    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    else:
        df = pd.DataFrame([entry])

    df.to_csv(LOG_PATH, index=False)
