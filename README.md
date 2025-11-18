# AI Prompt Safety Evaluator

A lightweight GenAI project that detects unsafe or harmful content in user prompts, identifies emotional distress, evaluates images, and automatically generates safer alternatives.

## Features

- Text safety analysis using Google Gemini API

- Emotional distress detection

- Image emotional risk analysis

- Risk categorization and color-coded recommendations

- Automatic safe rewrite suggestions

- Quick action cards with icons and color-coding

- Notifications via AWS SES

- Logging for monitoring

- Streamlit UI for easy interaction

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure
ai-safety-evaluator/
  ├── app.py                 # Streamlit user interface
  ├── safety_checker.py      # Core text risk analysis logic
  ├── fixer.py               # Prompt-fixing engine for unsafe inputs
  ├── logger.py              # Logging results to a CSV file
  ├── recommendations.py     # Recommended actions based on risk level
  ├── text_analyzer.py       # Emotional distress detection
  ├── image_analyzer.py      # Image emotional risk detection
  ├── notifier.py            # AWS SES notifications
  ├── requirements.txt       # Python dependencies
  ├── README.md              # Project overview and usage guide

> **Note:** The email notification feature (`notifier.py`) is partially configured — the email account and API keys have been set up, and a verification email was sent successfully. However, sending notifications from the app is still not working and requires further debugging.
