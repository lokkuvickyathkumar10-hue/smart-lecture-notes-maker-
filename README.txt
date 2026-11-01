SMART LECTURE NOTES MAKER

Run:
1. Install Python 3.10+
2. pip install -r requirements.txt
3. streamlit run app.py

Android-friendly publishing:
1. Extract this ZIP.
2. Upload app.py and requirements.txt to a GitHub repository.
3. Go to https://share.streamlit.io and sign in with GitHub.
4. Create app -> select repository -> branch main -> main file app.py -> Deploy.

Features: content-based notes, four methods, editable output, SQLite save/search/view/delete,
TXT/PDF downloads, summary and revision prompts. No AI API is connected.

Important: Streamlit Cloud's local SQLite file may reset during app restarts/redeployments.
Download important notes regularly. For reliable cloud persistence, connect a hosted database.
Use study material only; do not upload confidential data.
