import streamlit as st
from safety_checker import check_safety
from fixer import fix_text
from logger import log_event

st.set_page_config(page_title="AI Prompt Safety Evaluator")

st.title("AI Prompt Safety Evaluator")
st.write("Enter any text and evaluate its safety.")

text = st.text_area("Enter text here")

if st.button("Analyze"):
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        result = check_safety(text)
        st.subheader("Safety Result")
        st.json(result)

        log_event(text, result)

        if result.get("is_harmful", "").lower() == "yes":
            st.subheader("Safe Version")
            safe_output = fix_text(text)
            st.write(safe_output)
