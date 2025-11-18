import json
import re

import streamlit as st
from PIL import Image
from safety_checker import check_safety
from fixer import fix_text
from logger import log_event
from text_analyzer import analyze_text_for_distress
from image_analyzer import analyze_image_combined
from recommendations import get_support_recommendations
from notifier import notify_contact
import time
from google.genai.errors import ServerError, ClientError

st.set_page_config(page_title="AI Prompt Safety Evaluator")
st.title("AI Prompt Safety Evaluator")
st.write("Evaluate text and images for safety and emotional distress.")

# ------------------- Retry wrapper -------------------
def retry_api_call(func, *args, retries=3, delay=5, **kwargs):
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except ServerError:
            if i < retries - 1:
                time.sleep(delay)
            else:
                return {"error": "The AI model is currently overloaded. Please try again later."}
        except ClientError as e:
            return {"error": f"Client error occurred: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error occurred: {str(e)}"}

# ------------------- Helper functions -------------------
def risk_color(level: str):
    level = level.lower()
    if level == "high":
        return "red"
    elif level == "medium":
        return "orange"
    elif level == "low":
        return "green"
    else:
        return "gray"

def risk_progress(level: str):
    mapping = {"none":0, "low":0.33, "medium":0.66, "high":1.0}
    return mapping.get(level.lower(), 0)

# ------------------- Initialize session_state -------------------
if "combined_text" not in st.session_state:
    st.session_state.combined_text = ""
if "safety_result" not in st.session_state:
    st.session_state.safety_result = {}
if "safe_output" not in st.session_state:
    st.session_state.safe_output = ""
if "distress_result" not in st.session_state:
    st.session_state.distress_result = {}
if "quick_email" not in st.session_state:
    st.session_state.quick_email = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "image_result" not in st.session_state:
    st.session_state.image_result = {}

# ------------------- Tabs -------------------
tab1, tab2, tab3 = st.tabs([
    "Text Safety & Distress",
    "Image Analyzer",
    "Support & Notifications"
])

# ------------------- TAB 1: Text -------------------
with tab1:
    st.header("Text Safety & Distress Analyzer")
    st.session_state.combined_text = st.text_area(
        "Enter text for analysis",
        value=st.session_state.combined_text,
        key="combined_text_area"
    )

    if st.button("Analyze Text", key="analyze_combined_btn"):
        if not st.session_state.combined_text.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Analyzing..."):
                # Safety check
                st.session_state.safety_result = retry_api_call(check_safety, st.session_state.combined_text)
                if "error" in st.session_state.safety_result:
                    st.error(st.session_state.safety_result["error"])
                else:
                    # Safety card
                    color = "red" if st.session_state.safety_result.get("is_harmful", "").lower() == "yes" else "green"
                    st.markdown(f"<div style='padding:10px; border:2px solid {color}; border-radius:8px;'>"
                                f"<h4>Safety Result</h4>"
                                f"<p><b>Harmful:</b> {st.session_state.safety_result.get('is_harmful')}</p>"
                                f"<p><b>Category:</b> {st.session_state.safety_result.get('category', 'N/A')}</p>"
                                f"<p><b>Explanation:</b> {st.session_state.safety_result.get('explanation')}</p>"
                                f"</div>", unsafe_allow_html=True)
                    log_event(st.session_state.combined_text, st.session_state.safety_result)

                    # Safe Version Suggestions
                    if st.session_state.safety_result.get("is_harmful", "").lower() == "yes":
                        st.session_state.safe_output = retry_api_call(fix_text, st.session_state.combined_text)
                        if isinstance(st.session_state.safe_output, dict) and "error" in st.session_state.safe_output:
                            st.error(st.session_state.safe_output["error"])
                        else:
                            st.markdown(f"<div style='padding:10px; border:2px solid green; border-radius:8px;'>"
                                        f"<h4>Safe Version Suggestions</h4>"
                                        f"<p>{st.session_state.safe_output}</p>"
                                        f"</div>", unsafe_allow_html=True)

                # Distress detection
                st.session_state.distress_result = retry_api_call(analyze_text_for_distress, st.session_state.combined_text)

    # Show results if exist
    if st.session_state.distress_result:
        # result = st.session_state.distress_result
        # # Default only if result is empty or contains an error
        # if "error" in result or not result:
        #     sentiment = "Unknown – API unavailable"
        #     risk_level = "Unknown – API unavailable"
        #     explanation = result.get("error", "No data returned from API.")
        #     actions = []
        # else:
        #     # Use the actual values from the API, fallback only if None
        #     sentiment = result.get("sentiment") or "Unknown"
        #     risk_level = result.get("risk_level") or "Unknown"
        #     explanation = result.get("explanation") or "No explanation provided."
        #     actions = result.get("recommended_actions") or []
        result = st.session_state.distress_result or {}

        if "error" in result or not result:
            sentiment = "Unknown – API unavailable"
            risk_level = "Unknown – API unavailable"
            explanation = result.get("error", "No data returned from API.")
            actions = []
        else:
            # parse the raw_response JSON

            raw = result.get("raw_response", "")
            # remove ```json ... ``` to get a valid JSON
            clean_json_str = re.sub(r"```json\s*|```", "", raw, flags=re.IGNORECASE).strip()

            try:
                data = json.loads(clean_json_str)
                sentiment = data.get("sentiment", "Unknown")
                risk_level = data.get("risk_level", "Unknown")
                explanation = data.get("explanation", "No explanation provided.")
                actions = data.get("recommended_actions", [])
            except Exception as e:
                sentiment = "Unknown – parse error"
                risk_level = "Unknown – parse error"
                explanation = f"Failed to parse API response: {str(e)}"
                actions = []

        st.write("DEBUG: Distress API result:", result)

        color = risk_color(risk_level)
        st.markdown(f"<div style='padding:10px; border:2px solid {color}; border-radius:8px;'>"
                    f"<h4>Distress Detection Result</h4>"
                    f"<p><b>Sentiment:</b> {sentiment}</p>"
                    f"<p><b>Risk Level:</b> {risk_level}</p>"
                    f"<p><b>Explanation:</b> {explanation}</p>", unsafe_allow_html=True)

        st.progress(risk_progress(risk_level))

        if actions:
            st.markdown("<b>Recommended Actions:</b>", unsafe_allow_html=True)
            for i, action in enumerate(actions, 1):
                st.markdown(f"<b>{i}.</b> {action}", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Quick Actions
        st.markdown("### Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💡 Show Support Resources"):
                st.write(get_support_recommendations(risk_level.lower()))
        with col2:
            st.session_state.quick_email = st.text_input(
                "Enter email for notification", value=st.session_state.quick_email
            )
            if st.button("🔔 Notify Contact"):
                if st.session_state.quick_email:
                    msg = f"Alert: individual showing {risk_level} risk behavior."
                    notify_contact(st.session_state.quick_email, msg)
                    st.success("Notification sent!")

# ------------------- TAB 2: Image -------------------
with tab2:
    st.header("Image Emotional Risk Analyzer")
    uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="image_uploader")
    if uploaded:
        st.session_state.uploaded_image = uploaded
        st.session_state.image_result = retry_api_call(analyze_image_combined, Image.open(uploaded).convert("RGB"))

    if st.session_state.image_result:
        result = st.session_state.image_result
        if "error" in result:
            st.error(result["error"])
        else:
            top_label = result.get("emotion", {}).get("top_label", "N/A")
            top_prob = result.get("emotion", {}).get("top_prob", 0)
            explanation = result.get("emotion", {}).get("description", "")

            color = risk_color(top_label)
            st.markdown(f"<div style='padding:10px; border:2px solid {color}; border-radius:8px;'>"
                        f"<h4>Image Emotional Analysis</h4>"
                        f"<p><b>Most likely emotion/label:</b> {top_label} ({top_prob:.2f})</p>"
                        f"<p><b>Explanation:</b> {explanation}</p>"
                        f"</div>", unsafe_allow_html=True)

# ------------------- TAB 3: Recommendations & Alerts -------------------
with tab3:
    st.header("Recommendations & Alerts")
    level = st.selectbox("Risk level", ["none", "low", "medium", "high"], key="risk_level_select")
    st.write(get_support_recommendations(level))

    st.subheader("Notify Contact")
    email = st.text_input("Email", key="notify_email")
    msg = st.text_area("Message", key="notify_msg")
    if st.button("Send Alert", key="send_alert_btn"):
        try:
            notify_contact(email, msg)
            st.success("Alert sent successfully")
        except Exception as e:
            st.error(f"Failed to send alert: {str(e)}")



# import streamlit as st
# from PIL import Image
# from safety_checker import check_safety
# from fixer import fix_text
# from logger import log_event
# from text_analyzer import analyze_text_for_distress
# from image_analyzer import analyze_image_combined
# from recommendations import get_support_recommendations
# from notifier import notify_contact
# import time
# from google.genai.errors import ServerError, ClientError
#
# st.set_page_config(page_title="AI Prompt Safety Evaluator")
# st.title("AI Prompt Safety Evaluator")
# st.write("Evaluate text and images for safety and emotional distress.")
#
# # ------------------- Retry wrapper -------------------
# def retry_api_call(func, *args, retries=3, delay=5, **kwargs):
#     for i in range(retries):
#         try:
#             return func(*args, **kwargs)
#         except ServerError:
#             if i < retries - 1:
#                 time.sleep(delay)
#             else:
#                 return {"error": "The AI model is currently overloaded. Please try again later."}
#         except ClientError as e:
#             return {"error": f"Client error occurred: {str(e)}"}
#         except Exception as e:
#             return {"error": f"Unexpected error occurred: {str(e)}"}
#
# # ------------------- Helper for color and risk progress -------------------
# def risk_color(level: str):
#     level = level.lower()
#     if level == "high":
#         return "red"
#     elif level == "medium":
#         return "orange"
#     elif level == "low":
#         return "green"
#     else:
#         return "gray"
#
# def risk_progress(level: str):
#     mapping = {"none":0, "low":0.33, "medium":0.66, "high":1.0}
#     return mapping.get(level.lower(), 0)
#
# # ------------------- Tabs -------------------
# tab1, tab2, tab3 = st.tabs([
#     "Text Safety & Distress",
#     "Image Analyzer",
#     "Support & Notifications"
# ])
#
# # ------------------- TAB 1: Text -------------------
# with tab1:
#     st.header("Text Safety & Distress Analyzer")
#     combined_text = st.text_area("Enter text for analysis", key="combined_text_area")
#
#     if st.button("Analyze Text", key="analyze_combined_btn"):
#         if not combined_text.strip():
#             st.warning("Please enter some text.")
#         else:
#             with st.spinner("Analyzing..."):
#                 # Safety check
#                 safety_result = retry_api_call(check_safety, combined_text)
#                 if "error" in safety_result:
#                     st.error(safety_result["error"])
#                 else:
#                     color = "red" if safety_result.get("is_harmful", "").lower() == "yes" else "green"
#                     st.markdown(f"<div style='padding:10px; border:2px solid {color}; border-radius:8px;'>"
#                                 f"<h4>Safety Result</h4>"
#                                 f"<p><b>Harmful:</b> {safety_result.get('is_harmful')}</p>"
#                                 f"<p><b>Category:</b> {safety_result.get('category', 'N/A')}</p>"
#                                 f"<p><b>Explanation:</b> {safety_result.get('explanation')}</p>"
#                                 f"</div>", unsafe_allow_html=True)
#                     log_event(combined_text, safety_result)
#
#                     # Safe Version Suggestions
#                     if safety_result.get("is_harmful", "").lower() == "yes":
#                         safe_output = retry_api_call(fix_text, combined_text)
#                         if isinstance(safe_output, dict) and "error" in safe_output:
#                             st.error(safe_output["error"])
#                         else:
#                             st.markdown(f"<div style='padding:10px; border:2px solid green; border-radius:8px;'>"
#                                         f"<h4>Safe Version Suggestions</h4>"
#                                         f"<p>{safe_output}</p>"
#                                         f"</div>", unsafe_allow_html=True)
#
#                 # Distress detection
#                 distress_result = retry_api_call(analyze_text_for_distress, combined_text)
#                 if "error" in distress_result:
#                     st.error(distress_result["error"])
#                 else:
#                     sentiment = distress_result.get("sentiment", "Unknown")
#                     risk_level = distress_result.get("risk_level", "Unknown")
#                     explanation = distress_result.get("explanation", "")
#                     actions = distress_result.get("recommended_actions", [])
#
#                     # Display card
#                     color = risk_color(risk_level)
#                     st.markdown(f"<div style='padding:10px; border:2px solid {color}; border-radius:8px;'>"
#                                 f"<h4>Distress Detection Result</h4>"
#                                 f"<p><b>Sentiment:</b> {sentiment}</p>"
#                                 f"<p><b>Risk Level:</b> {risk_level}</p>"
#                                 f"<p><b>Explanation:</b> {explanation}</p>"
#                                 f"</div>", unsafe_allow_html=True)
#
#                     st.progress(risk_progress(risk_level))
#
#                     # Recommended Actions
#                     if actions:
#                         st.subheader("Recommended Actions")
#                         for i, action in enumerate(actions, 1):
#                             st.write(f"{i}. {action}")
#
#                     # ------------------- Quick Actions with Session State -------------------
#                     st.subheader("Quick Actions")
#                     if "show_support" not in st.session_state:
#                         st.session_state.show_support = False
#                     if "notify_sent" not in st.session_state:
#                         st.session_state.notify_sent = False
#
#                     support_col, notify_col = st.columns(2)
#
#                     # Show support resources button
#                     with support_col:
#                         if st.button("💡 Show Support Resources"):
#                             st.session_state.show_support = True
#
#                     if st.session_state.show_support:
#                         st.info(get_support_recommendations(risk_level.lower()))
#
#                     # Notify contact
#                     with notify_col:
#                         notify_email = st.text_input("Enter email for notification", key="notify_quick_email")
#                         if st.button("🔔 Notify Contact"):
#                             if notify_email:
#                                 msg = f"Alert: individual showing {risk_level} risk behavior."
#                                 try:
#                                     notify_contact(notify_email, msg)
#                                     st.session_state.notify_sent = True
#                                 except Exception as e:
#                                     st.error(f"Failed to send alert: {str(e)}")
#                             else:
#                                 st.warning("Please enter an email first.")
#
#                     if st.session_state.notify_sent:
#                         st.success("Notification sent successfully!")
#
# # ------------------- TAB 2: Image -------------------
# with tab2:
#     st.header("Image Emotional Risk Analyzer")
#     uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="image_uploader")
#
#     if uploaded:
#         image = Image.open(uploaded).convert("RGB")
#         result = retry_api_call(analyze_image_combined, image)
#
#         if "error" in result:
#             st.error(result["error"])
#         else:
#             top_label = result.get("emotion", {}).get("top_label", "N/A")
#             top_prob = result.get("emotion", {}).get("top_prob", 0)
#             explanation = result.get("emotion", {}).get("description", "")
#
#             color = risk_color(top_label)
#             st.markdown(f"<div style='padding:10px; border:2px solid {color}; border-radius:8px;'>"
#                         f"<h4>Image Emotional Analysis</h4>"
#                         f"<p><b>Most likely emotion/label:</b> {top_label} ({top_prob:.2f})</p>"
#                         f"<p><b>Explanation:</b> {explanation}</p>"
#                         f"</div>", unsafe_allow_html=True)
#
# # ------------------- TAB 3: Recommendations & Alerts -------------------
# with tab3:
#     st.header("Recommendations & Alerts")
#     level = st.selectbox("Risk level", ["none", "low", "medium", "high"], key="risk_level_select")
#     st.write(get_support_recommendations(level))
#
#     st.subheader("Notify Contact")
#     email = st.text_input("Email", key="notify_email")
#     msg = st.text_area("Message", key="notify_msg")
#     if st.button("Send Alert", key="send_alert_btn"):
#         if email.strip() and msg.strip():
#             try:
#                 notify_contact(email, msg)
#                 st.success("Alert sent successfully")
#             except Exception as e:
#                 st.error(f"Failed to send alert: {str(e)}")
#         else:
#             st.warning("Please enter both email and message before sending.")
#
#
#
# # import base64
# # from PIL import Image
# # import streamlit as st
# # from safety_checker import check_safety
# # from fixer import fix_text
# # from logger import log_event
# #
# # from text_analyzer import analyze_text_for_distress
# # from image_analyzer import analyze_image_combined
# # from recommendations import get_support_recommendations
# # from notifier import notify_contact
# #
# # st.set_page_config(page_title="AI Prompt Safety Evaluator")
# #
# # st.title("AI Prompt Safety Evaluator")
# # st.write("Enter any text and evaluate its safety.")
# #
# # text = st.text_area("Enter text here")
# #
# # if st.button("Analyze"):
# #     if not text.strip():
# #         st.warning("Please enter some text.")
# #     else:
# #         result = check_safety(text)
# #         st.subheader("Safety Result")
# #         st.json(result)
# #
# #         log_event(text, result)
# #
# #         if result.get("is_harmful", "").lower() == "yes":
# #             st.subheader("Safe Version")
# #             safe_output = fix_text(text)
# #             st.write(safe_output)
# #
# # # ---- EXISTING CODE REMAINS UNTOUCHED ----
# #
# # st.sidebar.title("New Safety Tools")
# #
# # tab1, tab2, tab3 = st.tabs([
# #     "Text Risk Analyzer",
# #     "Image Analyzer",
# #     "Support & Notifications"
# # ])
# #
# # with tab1:
# #     st.header("Text distress detection")
# #     user_text = st.text_area("Enter text")
# #     if st.button("Analyze", key="analyze_text_btn"):
# #         result = analyze_text_for_distress(user_text)
# #         st.json(result)
# # with tab2:
# #     st.header("Image Emotional Risk Analyzer")
# #     uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
# #
# #     if uploaded:
# #         image = Image.open(uploaded).convert("RGB")
# #
# #         result = analyze_image_combined(image)
# #
# #         st.subheader("Analysis Result")
# #
# #         st.json(result)
# #
# #         top_label = result["emotion"]["top_label"]
# #         top_prob = result["emotion"]["top_prob"]
# #         explanation = result["emotion"]["description"]
# #
# #         st.write(f"**Most likely emotion/label:** {top_label} ({top_prob:.2f})")
# #         st.write(f"**Simple explanation:** {explanation}")
# #
# # with tab3:
# #     st.header("Recommendations and alerts")
# #     level = st.selectbox("Risk level", ["none", "low", "medium", "high"])
# #     st.write(get_support_recommendations(level))
# #
# #     st.subheader("Notify contact")
# #     email = st.text_input("Email")
# #     msg = st.text_area("Message")
# #     if st.button("Send alert", key="send_alert_btn"):
# #         notify_contact(email, msg)
# #         st.success("Alert sent")
#
#
# # import base64
# # from PIL import Image
# # import streamlit as st
# # from safety_checker import check_safety
# # from fixer import fix_text
# # from logger import log_event
# #
# # from text_analyzer import analyze_text_for_distress
# # from image_analyzer import analyze_image_combined
# # from recommendations import get_support_recommendations
# # from notifier import notify_contact
# #
# # st.set_page_config(page_title="AI Prompt Safety Evaluator")
# #
# # st.title("AI Prompt Safety Evaluator")
# # st.write("Enter any text and evaluate its safety.")
# #
# # text = st.text_area("Enter text here")
# #
# # if st.button("Analyze"):
# #     if not text.strip():
# #         st.warning("Please enter some text.")
# #     else:
# #         result = check_safety(text)
# #         st.subheader("Safety Result")
# #         st.json(result)
# #
# #         log_event(text, result)
# #
# #         if result.get("is_harmful", "").lower() == "yes":
# #             st.subheader("Safe Version")
# #             safe_output = fix_text(text)
# #             st.write(safe_output)
# #
# # # ---- EXISTING CODE REMAINS UNTOUCHED ----
# #
# # st.sidebar.title("New Safety Tools")
# #
# # tab1, tab2, tab3 = st.tabs([
# #     "Text Risk Analyzer",
# #     "Image Analyzer",
# #     "Support & Notifications"
# # ])
# #
# # with tab1:
# #     st.header("Text distress detection")
# #     user_text = st.text_area("Enter text")
# #     if st.button("Analyze", key="analyze_text_btn"):
# #         result = analyze_text_for_distress(user_text)
# #         st.json(result)
# # with tab2:
# #     st.header("Image Emotional Risk Analyzer")
# #     uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
# #
# #     if uploaded:
# #         image = Image.open(uploaded).convert("RGB")
# #
# #         result = analyze_image_combined(image)
# #
# #         st.subheader("Analysis Result")
# #
# #         st.json(result)
# #
# #         top_label = result["emotion"]["top_label"]
# #         top_prob = result["emotion"]["top_prob"]
# #         explanation = result["emotion"]["description"]
# #
# #         st.write(f"**Most likely emotion/label:** {top_label} ({top_prob:.2f})")
# #         st.write(f"**Simple explanation:** {explanation}")
# #
# # with tab3:
# #     st.header("Recommendations and alerts")
# #     level = st.selectbox("Risk level", ["none", "low", "medium", "high"])
# #     st.write(get_support_recommendations(level))
# #
# #     st.subheader("Notify contact")
# #     email = st.text_input("Email")
# #     msg = st.text_area("Message")
# #     if st.button("Send alert", key="send_alert_btn"):
# #         notify_contact(email, msg)
# #         st.success("Alert sent")