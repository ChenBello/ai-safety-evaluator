# import streamlit as st
#
# st.title("Hello Streamlit!")
# st.write("אם את רואה את זה, הכל עובד")
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Init with API key
genai.configure(api_key=GOOGLE_API_KEY)


print(genai.list_models())
