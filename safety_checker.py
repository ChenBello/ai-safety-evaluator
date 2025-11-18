# safety_checker.py
import os
import json
import re
from google import genai  # Google AI Studio Python SDK

# Optional: load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

# Make sure you set your GOOGLE_API_KEY in environment variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Initialize the Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)


def check_safety(text):
    """
    Analyze a given text for potential safety risks using Google Gemini API.
    Returns: is_harmful, category, explanation
    """

    prompt = f"""
    You are a safety analysis tool.
    Respond ONLY with valid JSON, no explanation text outside the JSON.

    Example format:
    {{
        "is_harmful": "yes or no",
        "category": "violence, hate, self-harm, etc",
        "explanation": "short reason"
    }}

    Analyze this text: "{text}"
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw = response.text.strip()

        # Try direct JSON first
        try:
            return json.loads(raw)
        except:
            pass

        # Fallback: extract JSON part only
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass

        # If everything fails
        return {
            "is_harmful": "unknown",
            "category": "unknown",
            "explanation": "Parsing error"
        }

    except Exception as e:
        return {
            "is_harmful": "unknown",
            "category": "google_api_error",
            "explanation": str(e)
        }


# # Example usage
# if __name__ == "__main__":
#     text_to_check = "I want to harm someone"
#     result = check_safety(text_to_check)
#     print("Safety Result:", result)


# import os
# from dotenv import load_dotenv
# import openai
# import json
#
# load_dotenv()
# openai.api_key = os.environ.get("OPENAI_API_KEY")
#
#
# def check_safety(text):
#     """
#     Analyze a given text for potential safety risks using OpenAI API.
#     Returns a JSON-like dictionary with fields: is_harmful, category, explanation.
#     """
#
#     try:
#         system_prompt = (
#             "You are a safety analysis tool. "
#             "Return only a JSON dictionary with the fields: "
#             "is_harmful, category, explanation."
#         )
#
#         user_prompt = f"Analyze the following text for safety concerns. Text: {text}"
#
#         resp = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt}
#             ]
#         )
#
#         content = resp.choices[0].message.content
#
#         try:
#             return json.loads(content)
#         except json.JSONDecodeError:
#             return {
#                 "is_harmful": "unknown",
#                 "category": "unknown",
#                 "explanation": "Parsing error"
#             }
#
#     except openai.OpenAIError as e:  # Catch all OpenAI errors including rate limits
#         # You can inspect str(e) to differentiate quota vs other errors
#         return {
#             "is_harmful": "unknown",
#             "category": "openai_error",
#             "explanation": str(e)
#         }
#
# # def check_safety(text):
# #     system_prompt = (
# #         "You are a safety analysis tool. "
# #         "Return only a JSON dictionary with the fields: "
# #         "is_harmful, category, explanation."
# #     )
# #
# #     user_prompt = (
# #         f"Analyze the following text for safety concerns. "
# #         f"Text: {text}"
# #     )
# #
# #     resp = openai.chat.completions.create(
# #         model="gpt-3.5-turbo",
# #         messages=[
# #             {"role": "system", "content": system_prompt},
# #             {"role": "user", "content": user_prompt}
# #         ]
# #     )
# #
# #     content = resp.choices[0].message.content
# #
# #     try:
# #         return json.loads(content)
# #     except:
# #         return {
# #             "is_harmful": "unknown",
# #             "category": "unknown",
# #             "explanation": "Parsing error"
# #         }
#
# # def check_safety(text):
# #     prompt = f"""
# #     Analyze the following text and determine if it contains harmful content.
# #     Return a JSON with:
# #     - is_harmful: yes or no
# #     - category: type of harm
# #     - explanation: short explanation
# #
# #     Text: {text}
# #     """
# #
# #     response = openai.ChatCompletion.create(
# #         model="gpt-4o-mini",
# #         messages=[{"role": "user", "content": prompt}]
# #     )
# #
# #     return response.choices[0].message["content"]
#
