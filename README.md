# UC Berkeley Course Finder

Finds UC Berkeley courses matching a student's interests by scraping live listings and using Gemini AI to match and explain recommendations.

## How it works
- User enters their interests
- App scrapes [classes.berkeley.edu](https://classes.berkeley.edu) based on keywords
- Gemini ranks and explains the best course matches
- User downloads a PDF of recommendations

## How to run

1. Clone the repo
2. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
3. Create `.streamlit/secrets.toml` file:
    ```toml
    GEMINI_API_KEY = "your-gemini-api-key"
    ```
4. Run app locally:
    ```bash
    streamlit run app.py
    ```

## Deploy to Streamlit Cloud
- Push to GitHub
- Connect your repo
- Set `GEMINI_API_KEY` in Streamlit Cloud Secrets
