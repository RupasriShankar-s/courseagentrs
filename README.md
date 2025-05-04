# UC Berkeley Resume-to-Course Matcher

Match your resume to UC Berkeley courses and download a Berkeley-styled PDF with personalized recommendations.

## How it works
- Upload your resume (PDF only)
- App extracts your interests and experience
- Matches against Berkeley course catalog
- Gemini AI recommends and explains best courses
- Download a Berkeley-colored PDF report

## To Run Locally

1. Clone this repo
2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up `.streamlit/secrets.toml` with your Gemini API key:

    ```toml
    GEMINI_API_KEY = "your-gemini-api-key-here"
    ```

4. Run:

    ```bash
    streamlit run app.py
    ```

## Deploy to Streamlit Cloud

- Upload this repo
- Set your GEMINI_API_KEY in Secrets
- Deploy!

---
Built with ❤️ for UC Berkeley students.
