# # text_analyzer.py
# import os
# import json
# import time
#
# from dotenv import load_dotenv
# from vertexai.preview.generative_models import GenerativeModel
# import vertexai
# import google.generativeai as genai
#
# load_dotenv()
# GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
#
# # Init with API key
# genai.configure(api_key=GOOGLE_API_KEY)
#
# MODEL_NAME = "gemini-2.5-flash-lite"
#
#
# def analyze_text_for_distress(text, retries=3):
#     prompt = f"""
# You are a psychological safety evaluator.
# Analyze the following text and return ONLY valid JSON with the following fields:
#
# sentiment            // one of: positive, negative, neutral
# risk_level           // one of: none, low, medium, high
# explanation          // short description
# recommended_actions  // array of actions
#
# Text: {text}
#
# Return ONLY JSON, no other text.
# """
#
#     model = genai.GenerativeModel(MODEL_NAME)
#
#     for attempt in range(retries):
#         try:
#             response = model.generate_content(prompt)
#             raw = response.text
#
#             return json.loads(raw)
#
#         except Exception as e:
#             if attempt < retries - 1:
#                 time.sleep(1.5)
#                 continue
#
#             return {
#                 "sentiment": "unknown",
#                 "risk_level": "unknown",
#                 "explanation": f"Model failed: {str(e)}",
#                 "recommended_actions": []
#             }


# text_analyzer.py
import os
from dotenv import load_dotenv
import streamlit as st
from google import genai
import json

# Load API key from .env
load_dotenv()
# Make sure you set your GOOGLE_API_KEY in environment variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
# Client Definition
client = genai.Client(api_key=GOOGLE_API_KEY)

def analyze_text_for_distress(text):
#     prompt = f"""
# Analyze this text for emotional distress, self harm, violence, or urgent risk.
# Return JSON with fields:
# sentiment
# risk_level
# explanation
# recommended_actions
# Text: {text}
# """
    prompt = f"""
    You are a psychological safety evaluator.
    Analyze the following text and return ONLY valid JSON (Do not include any explanations, comments, or extra text) with the following fields:

    sentiment            // one of: positive, negative, neutral
    risk_level           // one of: none, low, medium, high
    explanation          // short description
    recommended_actions  // array of actions

    Text: {text}

    Return ONLY JSON, no other text.
    """

    chat = client.chats.create(model="gemini-2.5-flash")
    response = chat.send_message(prompt)

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"raw_response": response.text}

# # --- Streamlit UI ---
# st.title("Text Distress Detection")
#
# user_text = st.text_area("Enter text")
#
# if st.button("Analyze"):
#     if not user_text.strip():
#         st.warning("Please enter some text to analyze.")
#     else:
#         with st.spinner("Analyzing..."):
#             result = analyze_text_for_distress(user_text)
#
#         # show response
#         st.subheader("Analysis Result:")
#         if "raw_response" in result:
#             st.text(result["raw_response"])
#         else:
#             st.json(result)


# import openai
#
# def analyze_text_for_distress(text):
#     prompt = f"""
#     Analyze this text for emotional distress, self harm, violence, or urgent risk.
#     Return JSON with fields:
#     sentiment
#     risk_level
#     explanation
#     recommended_actions
#     Text: {text}
#     """
#
#     response = openai.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )
#
#     return response.choices[0].message.content
