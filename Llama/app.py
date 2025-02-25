# import os
# from dotenv import dotenv_values
# import streamlit as st
# from groq import Groq
# import pdfkit
# from docx import Document
# import speech_recognition as sr
# import pyttsx3
# from PIL import Image
# import pytesseract 

# engine = pyttsx3.init()
# def speak(text):
#     try:
#         engine = pyttsx3.init()
#         engine.say(text)
#         engine.runAndWait()
#         engine.stop()
#     except RuntimeError:
#         print("Speech engine is already running. Resetting engine.")
#         engine = pyttsx3.init()
#         engine.stop()

# def voice_input():
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         st.sidebar.write("Listening... Please speak your query.")
#         try:
#             audio = recognizer.listen(source, timeout=5)
#             query = recognizer.recognize_google(audio)
#             st.sidebar.write(f"You said: {query}")
#             return query
#         except sr.WaitTimeoutError:
#             st.sidebar.write("Listening timed out. Please try again.")
#         except sr.UnknownValueError:
#             st.sidebar.write("Sorry, I couldn't understand the audio.")
#         except Exception as e:
#             st.sidebar.write(f"Error: {str(e)}")
#     return None

# def parse_groq_stream(stream):
#     response_content = ""
#     for chunk in stream:
#         if chunk.choices and chunk.choices[0].delta.content is not None:
#             response_content += chunk.choices[0].delta.content
#             yield chunk.choices[0].delta.content
#     return response_content

# def extract_text_from_image(image_path):
#     image = Image.open(image_path)
#     text = pytesseract.image_to_string(image)
#     return text

# def extract_text_from_docx(docx_path):
#     doc = Document(docx_path)
#     return "\n".join([para.text for para in doc.paragraphs])

# def calculate_tax(income, regime):
#     tax_estimate = 0
#     if regime == "New Regime":
#         if income <= 400000:
#             tax_estimate = 0
#         elif income <= 800000:
#             tax_estimate = (income - 400000) * 0.05
#         elif income <= 1200000:
#             tax_estimate = 20000 + (income - 800000) * 0.10
#         elif income <= 1600000:
#             tax_estimate = 60000 + (income - 1200000) * 0.15
#         elif income <= 2000000:
#             tax_estimate = 120000 + (income - 1600000) * 0.20
#         elif income <= 2400000:
#             tax_estimate = 200000 + (income - 2000000) * 0.25
#         else:
#             tax_estimate = 300000 + (income - 2400000) * 0.30
#     else:
#         if income <= 250000:
#             tax_estimate = 0
#         elif income <= 500000:
#             tax_estimate = (income - 250000) * 0.05
#         elif income <= 1000000:
#             tax_estimate = 12500 + (income - 500000) * 0.20
#         else:
#             tax_estimate = 112500 + (income - 1000000) * 0.30
#     return round(tax_estimate, 2)

# def format_tax_breakdown(income, regime, total_deductions, taxable_income, tax_estimate):
#     breakdown = [
#         f"**Tax Calculation for Annual Income of ₹{income:,.2f} under the {regime}:**",
#         f"- Total Deductions Applied: ₹{total_deductions:,.2f}",
#         f"- Taxable Income after Deductions: ₹{taxable_income:,.2f}",
#         f"- Total Estimated Tax: ₹{tax_estimate:,.2f}"
#     ]
#     return "\n".join(breakdown)

# def export_chat_as_word():
#     doc = Document()
#     doc.add_heading("Tax Assistant Chat History", level=1)
#     for message in st.session_state.chat_history:
#         role = "User" if message["role"] == "user" else "Assistant"
#         doc.add_paragraph(f"{role}: {message['content']}")
#     file_path = "Tax_Assistant_Chat_History.docx"
#     doc.save(file_path)
#     return file_path

# # Streamlit page setup
# st.set_page_config(page_title="Tax Assistant 🧑‍💼", page_icon="💰", layout="centered")

# # Load environment variables
# try:
#     secrets = dotenv_values(".env")
#     GROQ_API_KEY = secrets["GROQ_API_KEY"]
# except Exception:
#     secrets = st.secrets
#     GROQ_API_KEY = secrets["GROQ_API_KEY"]

# os.environ["GROQ_API_KEY"] = GROQ_API_KEY
# INITIAL_RESPONSE = secrets.get("INITIAL_RESPONSE", "Hello! I’m here to help with tax finalization.")
# CHAT_CONTEXT = secrets.get("CHAT_CONTEXT", "You are a tax assistant helping users navigate tax finalization.")

# client = Groq(api_key=GROQ_API_KEY)

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = [{"role": "assistant", "content": INITIAL_RESPONSE}]

# # Main UI
# st.title("Welcome to Your Tax Assistant!")
# st.caption("Here to guide you through Indian tax finalization with ease.")

# for message in st.session_state.chat_history:
#     role = "user" if message["role"] == "user" else "assistant"
#     avatar = "🔨" if role == "user" else "🧑‍💼"
#     with st.chat_message(role, avatar=avatar):
#         st.markdown(message["content"])

# # File Upload Section
# uploaded_file = st.file_uploader("Upload Image or Document for Tax Calculation", type=["png", "jpg", "jpeg", "docx"])

# if uploaded_file:
#     with st.chat_message("user", avatar="📄"):
#         st.markdown(f"Uploaded: {uploaded_file.name}")
#     if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
#         extracted_text = extract_text_from_image(uploaded_file)
#     elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
#         extracted_text = extract_text_from_docx(uploaded_file)
#     else:
#         extracted_text = "Unsupported file type. Please upload a PNG, JPG, or DOCX file."

#     with st.chat_message("assistant", avatar="🧑‍💼"):
#         st.markdown(f"Extracted text: {extracted_text}")

# # User text or voice input
# col1, col2 = st.columns([3, 1])
# with col1:
#     user_prompt = st.chat_input("Ask me any tax-related question...")
# with col2:
#     if st.button("🎙 Speak Your Query"):
#         user_prompt = voice_input()

# # Sidebar for tax estimation
# st.sidebar.title("Additional Tools")
# st.sidebar.subheader("Tax Estimation")
# income = st.sidebar.number_input("Enter your annual income (INR):", min_value=0, step=10000)
# tax_regime = st.sidebar.radio("Select Tax Regime:", ("New Regime", "Old Regime"))

# # Deductions Section
# st.sidebar.subheader("Deductions Checklist")
# deductions = {
#     "80C (Investments)": st.sidebar.number_input("80C (Investments) - Max ₹1,50,000:", min_value=0, max_value=150000, step=1000),
#     "80D (Health Insurance)": st.sidebar.number_input("80D (Health Insurance) - Max ₹25,000:", min_value=0, max_value=25000, step=1000),
#     "80E (Education Loan Interest)": st.sidebar.number_input("80E (Education Loan Interest):", min_value=0, step=1000),
#     "Home Loan Principal": st.sidebar.number_input("Home Loan Principal - Max ₹2,00,000:", min_value=0, max_value=200000, step=1000)
# }

# total_deductions = sum(deductions.values())
# taxable_income = max(0, income - total_deductions)

# tax_estimate = calculate_tax(taxable_income, tax_regime)
# st.sidebar.write(f"**Total Deductions Applied:** ₹{total_deductions:,.2f}")
# st.sidebar.write(f"**Taxable Income after Deductions:** ₹{taxable_income:,.2f}")
# st.sidebar.write(f"**Estimated Tax after Deductions:** ₹{tax_estimate:,.2f}")

# st.sidebar.subheader("Tax Resources")
# st.sidebar.write("[Income Tax India](https://www.incometax.gov.in/iec/foportal)")
# st.sidebar.write("[Make Payment](https://eportal.incometax.gov.in/iec/foservices/#/e-pay-tax-prelogin/user-details)")

# if st.sidebar.button("🖨 Download Tax Report as Word"):
#     word_file_path = export_chat_as_word()
#     with open(word_file_path, "rb") as word_file:
#         st.sidebar.download_button(
#             label="Download Tax Report as Word",
#             data=word_file,
#             file_name="Tax_Assistant_Chat_History.docx",
#             mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#         )

# if user_prompt:
#     with st.chat_message("user", avatar="🔨"):
#         st.markdown(user_prompt)
#     st.session_state.chat_history.append({"role": "user", "content": user_prompt})

#     messages = [
#         {"role": "system", "content": CHAT_CONTEXT},
#         {"role": "assistant", "content": INITIAL_RESPONSE},
#         *st.session_state.chat_history,
#     ]

#     with st.chat_message("assistant", avatar="🧑‍💼"):
#         if user_prompt.lower().startswith("calculate tax"):
#             try:
#                 user_income = int(user_prompt.split()[-1])
#                 response_content = format_tax_breakdown(user_income, tax_regime, total_deductions, taxable_income, tax_estimate)
#             except ValueError:
#                 response_content = "Please provide a valid income amount for tax calculation."
#         else:
#             stream = client.chat.completions.create(
#                 model="llama3-8b-8192",
#                 messages=messages,
#                 stream=True
#             )
#             response_content = "".join(parse_groq_stream(stream))

#         st.markdown(response_content)
#         speak(response_content)
#     st.session_state.chat_history.append({"role": "assistant", "content": response_content})


import streamlit as st

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# Redirect to login page initially
st.switch_page("pages/login.py")
