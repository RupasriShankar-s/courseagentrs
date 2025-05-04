
import streamlit as st
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import google.generativeai as genai

# --- CONFIG ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]  # Set this in Streamlit secrets
genai.configure(api_key=GEMINI_API_KEY)

# --- FUNCTIONS ---

def scrape_courses(keyword):
    search_url = f"https://classes.berkeley.edu/search/class?page=0&f[0]=search_class_query%3A{keyword}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    course_blocks = soup.find_all('div', class_='search-result')
    courses = []

    for block in course_blocks:
        title = block.find('div', class_='class-title').text.strip() if block.find('div', class_='class-title') else "N/A"
        description = block.find('div', class_='description').text.strip() if block.find('div', class_='description') else "N/A"
        link = "https://classes.berkeley.edu" + block.find('a')['href'] if block.find('a') else "N/A"
        courses.append({
            'title': title,
            'description': description,
            'link': link
        })
    return courses

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
        st.write("Scraping Berkeley courses...")
        courses = scrape_courses(user_interest)

        if not courses:
            st.warning("No courses found. Try a different keyword.")
        else:
            st.success(f"Scraped {len(courses)} courses. Now asking Gemini for recommendations...")

            course_list_text = "\n".join([f"{c['title']}: {c['description']} ({c['link']})" for c in courses])
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
