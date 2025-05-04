
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from fpdf import FPDF
import google.generativeai as genai

# --- CONFIG ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# --- FUNCTIONS ---

def load_courses():
    return pd.read_csv("berkeley_courses.csv")

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def filter_courses(resume_text, courses_df):
    matches = []
    resume_text = resume_text.lower()

    for _, row in courses_df.iterrows():
        if resume_text and (row['title'].lower() in resume_text or row['description'].lower() in resume_text):
            matches.append(row.to_dict())
    return matches

def match_courses_with_gemini(resume_text, courses):
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
You are an academic advisor at UC Berkeley.

The student's resume text is:
"""
{resume_text}
"""

Here is a list of available courses (Title, Description, Link):
{courses}

Task:
- Select the 5–10 courses that best match the student's resume content.
- For each course, write 1–2 sentences explaining WHY it matches their background and interests.
- Mention keywords from the resume and course description where possible.

Format:

1. Course Title
   - Why it matches
   - Link
"""
    response = model.generate_content(prompt)
    return response.text

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2 ,4))

def create_stylized_pdf(gemini_output):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)

    # Berkeley Blue title
    r, g, b = hex_to_rgb("#003262")
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 15, "UC Berkeley Course Recommendations", ln=True, align="C")

    pdf.ln(5)
    pdf.set_font("Arial", "", 12)

    lines = gemini_output.split('\n')
    for line in lines:
        if line.strip().startswith(tuple(str(i) for i in range(1, 11))):  # New course
            pdf.ln(5)
            r, g, b = hex_to_rgb("#FDB515")  # California Gold
            pdf.set_text_color(r, g, b)
            pdf.set_font("Arial", "B", 14)
            pdf.multi_cell(0, 10, line.strip())
            pdf.set_font("Arial", "", 12)
            pdf.set_text_color(0, 0, 0)
        else:
            pdf.multi_cell(0, 10, line.strip())

    pdf_path = "/tmp/stylized_matching_courses.pdf"
    pdf.output(pdf_path)
    return pdf_path

# --- STREAMLIT APP ---

st.title("📄 UC Berkeley Resume-to-Courses Matcher")

uploaded_resume = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

if st.button("Find Matching Courses"):
    if uploaded_resume:
        st.write("Extracting resume text...")
        resume_text = extract_text_from_pdf(uploaded_resume)

        st.write("Loading Berkeley courses...")
        courses_df = load_courses()

        st.write("Matching courses based on your resume...")
        matched_courses = filter_courses(resume_text, courses_df)

        if not matched_courses:
            st.warning("No strong course matches found based on your resume. Try refining it!")
        else:
            st.success(f"Found {len(matched_courses)} initial matches. Asking Gemini for the best recommendations...")

            course_list_text = "\n".join([f"{c['title']}: {c['description']} ({c['link']})" for c in matched_courses])
            gemini_output = match_courses_with_gemini(resume_text, course_list_text)

            st.write("✅ Gemini generated personalized course recommendations!")

            pdf_path = create_stylized_pdf(gemini_output)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📄 Download Your Berkeley-Styled Course Recommendations",
                    data=f,
                    file_name="recommended_courses.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("Please upload your resume first!")
