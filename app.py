import streamlit as st
from langchain_groq import ChatGroq
import os
import PyPDF2
import warnings



st.set_page_config(page_title="Fashion Startup Advisor", page_icon="🧵", layout="centered")
st.title("🧵 Fashion Startup Advisor")
st.markdown("Ask anything about launching or growing your fashion brand — from design and sourcing to branding, e-commerce, and marketing.")

# Sidebar: API Key Input
with st.sidebar:
    st.header("🔐 API Key")
    api_key = st.text_input("Enter your Groq API Key", type="password")
    st.markdown("Don't have one? [Get it here](https://platform.openai.com/account/api-keys)")

    # PDF Upload
    st.header("📎 Upload Business Plan / Moodboard (PDF)")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    extracted_pdf_text = ""
    if uploaded_file:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        extracted_pdf_text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        st.success("PDF content loaded into assistant memory.")

# Exit if no key
if not api_key:
    st.warning("Please enter your Groq API Key in the sidebar.")
    st.stop()

# System prompt
system_prompt = f"""
You are a seasoned fashion startup advisor assisting founders, designers, and entrepreneurs in launching and growing fashion businesses. 
You have deep expertise in fashion branding, product development, sourcing, e-commerce, marketing, and sustainable fashion practices. 
Your tone is professional, insightful, and encouraging — like a trusted advisor who combines creative vision with strategic business thinking.

You help users:
- Define and refine their brand identity
- Design product lines with market fit
- Find ethical and affordable manufacturing options
- Develop pricing and positioning strategies
- Build and scale e-commerce platforms
- Launch creative marketing campaigns
- Stay informed about fashion trends and customer behavior
- Navigate logistics, funding, and legal setup

If the user has uploaded a document, refer to its contents for context. Here’s the extracted text:
\"\"\"
{extracted_pdf_text[:3000]}  # Limit token size for stability
\"\"\"

Ask clarifying questions if needed. Offer detailed, actionable advice. Suggest tools, platforms, or examples when relevant. Always keep the user's budget, goals, and brand identity in mind.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# Stage-based suggestions
st.markdown("🔍 **Select your current startup stage:**")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Ideation"):
        st.session_state.user_input = "I'm in the ideation phase. Help me define my brand and product vision."
with col2:
    if st.button("Production"):
        st.session_state.user_input = "I'm ready for production. How do I find reliable manufacturers and manage quality?"
with col3:
    if st.button("Launch"):
        st.session_state.user_input = "I’m preparing to launch. What’s a solid go-to-market strategy?"
with col4:
    if st.button("Growth"):
        st.session_state.user_input = "How do I scale my brand and increase repeat sales?"

# User text input
user_input = st.text_input("💬 Ask your question here:", key="user_input")

# Function to get OpenAI chat response
def get_chat_response(api_key, messages):
    # Initialize ChatGroq with the model name and API key
    client = ChatGroq(
        api_key=api_key,
        model_name="gemma2-9b-it", # Specify the model during initialization
        temperature=0.7
        # verbose=True # Add if needed and supported by ChatGroq constructor
    )
    # Use the invoke method for a standard LangChain ChatModel call
    response = client.invoke(messages)
    # The response object has a 'content' attribute
    return response.content

# Setup a one-time rerun flag
if "rerun_flag" not in st.session_state:
    st.session_state.rerun_flag = False

if user_input and not st.session_state.rerun_flag:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Styling your response..."):
        response = get_chat_response(api_key, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.rerun_flag = True
    st.rerun()

# Reset rerun flag after rerun
if st.session_state.rerun_flag:
    st.session_state.rerun_flag = False


# Display conversation history
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"🧍 **You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"🧵 **Advisor:** {msg['content']}")
