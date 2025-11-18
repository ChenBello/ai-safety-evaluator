# fixer.py
import os
from dotenv import load_dotenv
from google import genai  # Google AI Studio Python SDK

# Load API key from .env
load_dotenv()

# Create a client using your API key
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def fix_text(text):
    """
    Receives a potentially unsafe text and returns a safer, neutral version.
    Uses Gemini model and returns plain text.
    """
    prompt = f"""
    The following text may be unsafe or harmful.
    Rewrite it in a safe, calm and neutral way while keeping the meaning clear.

    Text: {text}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # or "gemini-2.5-pro"
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"Error: {str(e)}"



# import os
# import openai
# from dotenv import load_dotenv
#
# # openai.api_key = os.environ.get("OPENAI_API_KEY")
# load_dotenv()  # loads the variables from .env
# openai.api_key = os.environ.get("OPENAI_API_KEY")
#
# # openai.api_key = "YOUR_API_KEY"
# #
# # def fix_text(text):
# #     prompt = (
# #         f"The following text may contain unsafe content. "
# #         f"Rewrite it in a safer and neutral format while keeping the meaning clear. "
# #         f"Text: {text}"
# #     )
#
# def fix_text(text):
#     prompt = f"""
#     The following text has been detected as potentially unsafe.
#     Return a safe rewritten version while keeping the meaning neutral.
#
#     Text: {text}
#     """
#
#     response = openai.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": prompt}]
#     )
#
#     return response.choices[0].message.content
