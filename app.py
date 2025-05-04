# app.py
import streamlit as st
import pandas as pd
from fpdf import FPDF
import google.generativeai as genai

# --- CONFIG ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]  # Set this in Streamlit secrets
genai.configure(api_key=GEMINI_API_KEY)

# --- FUNCTIONS ---

def load_courses():
    return pd.read_csv("berkeley_courses.csv")

def filter_courses(user_interest, courses_df):
    matches = []
    user_interest = user_interest.lower()

    for _, row in courses_df.iterrows():
        if user_interest in row['description'].lower() or user_interest in row['title'].lower():
            matches.append(row.to_dict())
    return matches

def match_courses_with_gemini(user_interest, courses):
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
You are an academic advisor at UC Berkeley.

The student is interested in: "{user_interest}"

Here is a list of available courses (Title, Description, Link):
{courses}

Task:
- Select the 5–10 courses that best match the student's interests.
- For each course, write 1–2 sentences explaining WHY it matches their interests.
- Mention keywords from the interest and course description where possible.

Format:

1. Course Title
   - Why it matches
   - Link
"""
    response = model.generate_content(prompt)
    return response.text

def create_pdf(gemini_output):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in gemini_output.split('\n'):
        pdf.multi_cell(0, 10, line)
        pdf.ln()

    pdf_path = "/tmp/matching_courses.pdf"
    pdf.output(pdf_path)
    return pdf_path

# --- STREAMLIT APP ---

st.title("📚 UC Berkeley Course Finder")

user_interest = st.text_input("Enter your academic interests (e.g., AI, entrepreneurship, sustainability):")

if st.button("Find Matching Courses"):
    if user_interest:
        st.write("Loading Berkeley courses...")
        courses_df = load_courses()

        matched_courses = filter_courses(user_interest, courses_df)

        if not matched_courses:
            st.warning("No matching courses found. Try a different keyword.")
        else:
            st.success(f"Found {len(matched_courses)} matching courses. Now asking Gemini for recommendations...")

            course_list_text = "\n".join([f"{c['title']}: {c['description']} ({c['link']})" for c in matched_courses])
            gemini_output = match_courses_with_gemini(user_interest, course_list_text)

            st.write("✅ Gemini generated course recommendations!")

            pdf_path = create_pdf(gemini_output)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📄 Download your Course Recommendations PDF",
                    data=f,
                    file_name="recommended_courses.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("Please enter your interests first.")
