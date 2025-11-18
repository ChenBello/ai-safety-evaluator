# AI Prompt Safety Evaluator

A lightweight GenAI project that detects unsafe or harmful content in user prompts and automatically generates safer alternatives.

## Features
- Safety analysis using LLM
- Categorization of risk
- Automatic safe rewrite
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
  ├── safety_checker.py      # Core risk analysis logic
  ├── fixer.py               # Prompt-fixing engine for unsafe inputs
  ├── logger.py              # Logging results to a CSV file
  ├── requirements.txt       # Python dependencies
  ├── README.md              # Project overview and usage guide


ai-safety-evaluator/
  ├── app.py
  ├── safety_checker.py
  ├── fixer.py
  ├── logger.py
  ├── recommendations.py     ← חדש
  ├── text_analyzer.py       ← חדש
  ├── image_analyzer.py      ← חדש
  ├── notifier.py            ← חדש
  ├── requirements.txt
  ├── README.md