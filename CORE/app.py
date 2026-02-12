import streamlit as st
from paper_ingest import extract_text_from_pdf, fetch_arxiv_pdf
from embedder import chunk_text, embed_text
from llm_interface import ask_ollama
import tempfile
import time
import streamlit.components.v1 as components

# --- IMPROVED DARK THEME WITH BETTER TEXT VISIBILITY ---
st.markdown("""
    <style>
    .stApp {
        background: #0d0817 !important;
    }
    body, .stApp { 
        color: #ffffff !important; 
        background: #0d0817 !important;
    }
    h1, h2, h3, .stTitle { 
        color: #ffffff !important; 
        text-shadow: 0 2px 12px rgba(0,0,0,0.5);
    }
    p, .stMarkdown, .stText {
        color: #e8e8e8 !important;
    }
    .banner {
        background: linear-gradient(90deg, #1a1a3e 0%, #6a4c93 100%);
        color: #ffffff;
        padding: 18px 30px;
        border-radius: 20px;
        font-size: 1.3em;
        box-shadow: 0 4px 24px 0 rgba(106, 76, 147, 0.25);
        margin-bottom: 22px;
        text-align: center;
        font-weight: bold;
        letter-spacing: 1px;
    }
    .section-card {
        background: #1a1228;
        border-radius: 18px;
        box-shadow: 0 4px 24px 0 rgba(106, 76, 147, 0.2);
        padding: 18px;
        margin-bottom: 18px;
        border: 1px solid #2d1b4e;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6a4c93 0%, #1a1a3e 100%);
        color: #ffffff !important;
        border-radius: 25px;
        border: none;
        padding: 0.65em 2.2em;
        font-size: 1.13em;
        font-weight: bold;
        box-shadow: 0 4px 16px rgba(106, 76, 147, 0.3);
        transition: transform 0.2s;
        margin-bottom: 10px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #8b7bb8 0%, #2d1b4e 100%);
        color: #ffffff !important;
        transform: scale(1.05);
        box-shadow: 0 8px 32px rgba(106, 76, 147, 0.4);
    }
    .stTextArea textarea {
        background: #0f0a1a !important;
        color: #ffffff !important;
        border: 2px solid #6a4c93 !important;
        border-radius: 10px;
        font-size: 1.09em;
        font-family: 'Roboto', monospace;
    }
    .stTextInput input {
        background: #0f0a1a !important;
        color: #ffffff !important;
        border: 2px solid #6a4c93 !important;
        border-radius: 10px;
        font-size: 1.05em;
    }
    .stSelectbox {
        background: #1a1228 !important;
        color: #ffffff !important;
    }
    .stRadio {
        color: #ffffff !important;
    }
    .css-1d391kg, .css-1v0mbdj, .stSidebar {
        background: linear-gradient(135deg, #1a1a3e 0%, #3d2d5f 100%) !important;
        color: #ffffff !important;
    }
    .stSidebar .stMarkdown {
        color: #ffffff !important;
    }
    .stInfo {
        background: #1a3a4e;
        border-left: 4px solid #00d4ff;
        color: #ffffff !important;
        border-radius: 8px;
    }
    .stSuccess {
        background: #1a3a2e;
        border-left: 4px solid #00ff88;
        color: #ffffff !important;
        border-radius: 8px;
    }
    .stError {
        background: #3a1a1e;
        border-left: 4px solid #ff3366;
        color: #ffffff !important;
        border-radius: 8px;
    }
    .stWarning {
        background: #3a3a1a;
        border-left: 4px solid #ffaa00;
        color: #ffffff !important;
        border-radius: 8px;
    }
    .help-icon {
        font-size: 1.1em;
        vertical-align: middle;
        margin-left: 6px;
        cursor: pointer;
        color: #00d4ff;
    }
    .copy-btn {
        background: #6a4c93; 
        color: #ffffff; 
        border: none; 
        border-radius: 8px; 
        padding: 5px 15px; 
        font-weight: bold; 
        cursor: pointer; 
        margin-top: 5px; 
        margin-bottom: 10px;
    }
    .copy-btn:hover {
        background: #8b7bb8;
    }
    .download-btn {
        background: #6a4c93; 
        color: #ffffff; 
        border: none; 
        border-radius: 8px; 
        padding: 5px 15px; 
        font-weight: bold; 
        cursor: pointer; 
        margin-top: 5px; 
        margin-bottom: 10px;
    }
    .download-btn:hover {
        background: #8b7bb8;
    }
    .stExpander {
        background: #1a1228;
        border: 1px solid #2d1b4e;
        border-radius: 8px;
    }
    .stMetric {
        background: #1a1228;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Roboto:wght@400&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- Sidebar Branding & Navigation ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/992/992700.png", width=60)
st.sidebar.markdown('<div class="banner">🧑‍🔬 <b>PaperPilot</b></div>', unsafe_allow_html=True)
nav = st.sidebar.radio("Navigate", ["Home", "Upload/Fetch", "AI Actions", "History", "Settings"])
st.sidebar.markdown("**Instructions:**\n- Upload or fetch a paper\n- Preview extraction\n- Try AI actions!\n\n---\n**Made by AlgoWarriors**")

# --- Language Selector: Indian Languages Added ---
language = st.sidebar.selectbox(
    "🌐 Language",
    [
        "English",
        "Hindi",
        "Tamil",
        "Telugu",
        "Kannada",
        "Malayalam",
        "Bengali",
        "Marathi",
        "Gujarati",
        "Punjabi"
    ]
)

# Simple Language Dictionary Demo (Indian Regional Languages)
lang_dict = {
    "English": {
        "welcome": "Welcome to PaperPilot!",
        "upload": "Upload or Fetch a Paper",
        "actions": "AI Actions",
        "history": "Your History",
        "settings": "Settings",
        "paper": "Paper",
        "preview": "Preview Extracted Text",
        "ai_actions": "AI Actions"
    },
    "Hindi": {
        "welcome": "पेपरपायलट में आपका स्वागत है!",
        "upload": "पेपर अपलोड या प्राप्त करें",
        "actions": "एआई क्रियाएँ",
        "history": "आपका इतिहास",
        "settings": "सेटिंग्स",
        "paper": "पेपर",
        "preview": "निष्कर्षित पाठ का पूर्वावलोकन",
        "ai_actions": "एआई क्रियाएँ"
    },
    "Tamil": {
        "welcome": "PaperPilot-க்கு வரவேற்கிறோம்!",
        "upload": "ஆவணத்தை பதிவேற்றவும் அல்லது பெறவும்",
        "actions": "AI செயல்கள்",
        "history": "உங்கள் வரலாறு",
        "settings": "அமைப்புகள்",
        "paper": "ஆவணம்",
        "preview": "பிரித்தெடுக்கப்பட்ட உரையின் முன்னோட்டம்",
        "ai_actions": "AI செயல்கள்"
    },
    "Telugu": {
        "welcome": "పేపర్ పైలట్‌కు స్వాగతం!",
        "upload": "పేపర్‌ను అప్‌లోడ్ చేయండి లేదా పొందండి",
        "actions": "AI చర్యలు",
        "history": "మీ చరిత్ర",
        "settings": "సెట్టింగ్స్",
        "paper": "పేపర్",
        "preview": "ఎక్స్‌ట్రాక్ట్ చేసిన టెక్స్ట్ ప్రివ్యూ",
        "ai_actions": "AI చర్యలు"
    },
    "Kannada": {
        "welcome": "ಪೇಪರ್ ಪೈಲಟ್‌ಗೆ ಸ್ವಾಗತ!",
        "upload": "ಪೇಪರ್ ಅಪ್‌ಲೋಡ್ ಅಥವಾ ಪಡೆಯಿರಿ",
        "actions": "AI ಕ್ರಿಯೆಗಳು",
        "history": "ನಿಮ್ಮ ಇತಿಹಾಸ",
        "settings": "ಸೆಟ್ಟಿಂಗ್ಸ್",
        "paper": "ಪೇಪರ್",
        "preview": "ಹೊರತೆಗೆಯಲಾದ ಪಠ್ಯದ ಪೂರ್ವದೃಷ್ಟಿ",
        "ai_actions": "AI ಕ್ರಿಯೆಗಳು"
    },
    "Malayalam": {
        "welcome": "പേപ്പർ പൈലറ്റിലേക്ക് സ്വാഗതം!",
        "upload": "പേപ്പർ അപ്‌ലോഡ് ചെയ്യുക അല്ലെങ്കിൽ നേടുക",
        "actions": "AI പ്രവർത്തനങ്ങൾ",
        "history": "നിങ്ങളുടെ ചരിത്രം",
        "settings": "ക്രമീകരണങ്ങൾ",
        "paper": "പേപ്പർ",
        "preview": "നിര്വചിച്ച ടെക്സ്റ്റിന്റെ പ്രിവ്യൂ",
        "ai_actions": "AI പ്രവർത്തനങ്ങൾ"
    },
    "Bengali": {
        "welcome": "PaperPilot-এ স্বাগতম!",
        "upload": "পেপার আপলোড করুন বা সংগ্রহ করুন",
        "actions": "AI কার্যাবলী",
        "history": "আপনার ইতিহাস",
        "settings": "সেটিংস",
        "paper": "পেপার",
        "preview": "এক্সট্রাক্টেড টেক্সটের পূর্বরূপ",
        "ai_actions": "AI কার্যাবলী"
    },
    "Marathi": {
        "welcome": "PaperPilot मध्ये स्वागत आहे!",
        "upload": "पेपर अपलोड करा किंवा मिळवा",
        "actions": "AI क्रिया",
        "history": "तुमचा इतिहास",
        "settings": "सेटिंग्ज",
        "paper": "पेपर",
        "preview": "निघालेले मजकूर पूर्वावलोकन",
        "ai_actions": "AI क्रिया"
    },
    "Gujarati": {
        "welcome": "PaperPilot માં આપનું સ્વાગત છે!",
        "upload": "પેપર અપલોડ કરો અથવા મેળવો",
        "actions": "AI ક્રિયાઓ",
        "history": "તમારો ઇતિહાસ",
        "settings": "સેટિંગ્સ",
        "paper": "પેપર",
        "preview": "એક્સટ્રાક્ટ કરેલ ટેક્સ્ટનું પૂર્વદર્શન",
        "ai_actions": "AI ક્રિયાઓ"
    },
    "Punjabi": {
        "welcome": "PaperPilot ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ!",
        "upload": "ਪੇਪਰ ਅੱਪਲੋਡ ਕਰੋ ਜਾਂ ਲਵੋ",
        "actions": "AI ਕਾਰਵਾਈਆਂ",
        "history": "ਤੁਹਾਡਾ ਇਤਿਹਾਸ",
        "settings": "ਸੈਟਿੰਗਜ਼",
        "paper": "ਪੇਪਰ",
        "preview": "ਕੱਢਿਆ ਹੋਇਆ ਪਾਠ ਪੂਰਵਵਿੱਚ",
        "ai_actions": "AI ਕਾਰਵਾਈਆਂ"
    }
}

# --- Session State for History ---
if 'history' not in st.session_state:
    st.session_state.history = []

if 'paper_text' not in st.session_state:
    st.session_state.paper_text = ""
if 'paper_title' not in st.session_state:
    st.session_state.paper_title = ""

def reset_paper():
    st.session_state.paper_text = ""
    st.session_state.paper_title = ""

def add_to_history(title, text):
    st.session_state.history.append({'title': title, 'text': text})

def download_text(text, filename):
    st.download_button("Download Output", text, file_name=filename, key=filename, help="Download the generated output.")

# --- Only show one section at a time ---
st.markdown('<div class="banner">🚀 Scientific Research LLM Assistant<br><span style="font-size:1rem;">Accelerate your discoveries with AI-powered reading & writing!</span></div>', unsafe_allow_html=True)

if nav == "Home":
    st.markdown(f"<h2>{lang_dict[language]['welcome']}</h2>", unsafe_allow_html=True)
    st.info("This is the home screen. Use the sidebar to navigate.")

elif nav == "Upload/Fetch":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"1️⃣ {lang_dict[language]['upload']}")
    upload_option = st.radio("Choose input method:", ["📤 Upload PDF", "🌐 Fetch from arXiv"])

    # Tooltip help icon
    st.markdown("Upload a PDF <span class='help-icon' title='Supported: standard scientific PDFs.'>❓</span>", unsafe_allow_html=True)

    if upload_option == "📤 Upload PDF":
        uploaded_file = st.file_uploader("Upload a PDF", type="pdf", on_change=reset_paper)
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            try:
                st.session_state.paper_text = extract_text_from_pdf(tmp_file_path)
                st.session_state.paper_title = uploaded_file.name
                st.success(f"PDF '{uploaded_file.name}' uploaded and extracted.")
                add_to_history(st.session_state.paper_title, st.session_state.paper_text)
            except Exception as e:
                st.error(f"Failed to extract text from PDF: {e}")
    elif upload_option == "🌐 Fetch from arXiv":
        query = st.text_input("Enter arXiv search query or paper title/ID")
        # Autocomplete suggestion box
        if query:
            st.markdown("Recent queries: <span style='color:#00d4ff;'>arXiv:2309.00123, arXiv:2205.12345</span>", unsafe_allow_html=True)
        if st.button("Fetch Paper"):
            with st.spinner("🔄 Fetching from arXiv..."):
                st.progress(0)
                for percent_complete in range(1, 101, 10):
                    time.sleep(0.03)
                    st.progress(percent_complete)
                try:
                    pdf_path, title, paper = fetch_arxiv_pdf(query)
                    if pdf_path:
                        st.session_state.paper_text = extract_text_from_pdf(pdf_path)
                        st.session_state.paper_title = title
                        st.success(f"Fetched: {title}")
                        add_to_history(st.session_state.paper_title, st.session_state.paper_text)
                    else:
                        st.session_state.paper_text = ""
                        st.session_state.paper_title = ""
                        st.error("No paper found for that query!")
                except Exception as e:
                    st.session_state.paper_text = ""
                    st.session_state.paper_title = ""
                    st.error(f"Error fetching or extracting arXiv paper: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Preview Extracted Text ---
    if st.session_state.paper_text:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader(f"2️⃣ {lang_dict[language]['preview']}")
        st.markdown(
            f"<span style='font-size:1.5em; font-weight:700; color:#ffffff;'>{lang_dict[language]['paper']}: {st.session_state.paper_title}</span>",
            unsafe_allow_html=True
        )
        st.text_area("Extracted Text (first 800 chars)", st.session_state.paper_text[:800], height=180)
        with st.expander("📖 Show full extracted text"):
            st.write(st.session_state.paper_text)
        st.markdown('</div>', unsafe_allow_html=True)

elif nav == "AI Actions":
    if st.session_state.paper_text:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader(f"3️⃣ {lang_dict[language]['ai_actions']}")
        chunks = chunk_text(st.session_state.paper_text)

        def run_ollama_action(prompt, spinner_message, output_label, filename="output.txt"):
            try:
                with st.spinner(spinner_message):
                    output = ask_ollama(prompt)
                st.markdown(f"**{output_label}:**")
                st.markdown(
                    f"<div style='background:#0f0a1a;border-radius:10px;padding:12px;margin-bottom:10px;color:#ffffff;border:1px solid #6a4c93;'>{output}</div>",
                    unsafe_allow_html=True
                )
                # Copy to clipboard button (JS hack)
                components.html(f"""
                <button class="copy-btn" onclick="navigator.clipboard.writeText(`{output.replace("`", "\\`")}`)">Copy Output</button>
                """, height=40)
                download_text(output, filename)
            except Exception as e:
                st.error(f"Error communicating with Ollama: {e}")

        ai_col1, ai_col2 = st.columns(2)

        with ai_col1:
            st.markdown("##### 🧪 Generate Hypothesis <span class='help-icon' title='Suggest a novel research hypothesis based on your paper.'>❓</span>", unsafe_allow_html=True)
            if st.button("Generate Hypothesis"):
                prompt = (
                    f"Read this research paper and suggest a novel research hypothesis. "
                    f"Paper content:\n{st.session_state.paper_text[:2000]}"
                )
                run_ollama_action(prompt, "✨ Ollama is thinking...", "Hypothesis Suggestion", "hypothesis.txt")

            st.markdown("##### 💡 Grant Proposal <span class='help-icon' title='Draft a grant proposal based on your paper.'>❓</span>", unsafe_allow_html=True)
            if st.button("Draft Grant Proposal"):
                prompt = (
                    f"Based on this research paper, draft a brief grant proposal. "
                    f"Include motivation, objectives, and expected outcomes. "
                    f"Paper content:\n{st.session_state.paper_text[:2000]}"
                )
                run_ollama_action(prompt, "💸 Ollama is drafting proposal...", "Grant Proposal Draft", "grant_proposal.txt")

        with ai_col2:
            st.markdown("##### 📝 Literature Review <span class='help-icon' title='Get a concise literature review.'>❓</span>", unsafe_allow_html=True)
            if st.button("Automate Literature Review"):
                prompt = (
                    f"Write a concise literature review based on this paper. "
                    f"Focus on research gaps and opportunities. "
                    f"Paper content:\n{st.session_state.paper_text[:2000]}"
                )
                run_ollama_action(prompt, "📚 Ollama is generating a literature review...", "Literature Review", "literature_review.txt")

            st.markdown("##### 🔍 Ask About the Paper <span class='help-icon' title='Ask any question about the loaded paper.'>❓</span>", unsafe_allow_html=True)
            question = st.text_input("Your question about the paper")
            if st.button("Get Answer") and question.strip():
                prompt = f"Answer this question about the following paper:\nQuestion: {question}\nPaper content:\n{st.session_state.paper_text[:2000]}"
                run_ollama_action(prompt, "🤖 Ollama is answering...", "Answer", "answer.txt")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Please upload a PDF or fetch a paper from arXiv to enable AI actions.")

elif nav == "History":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"📜 {lang_dict[language]['history']}")
    if st.session_state.history:
        for entry in st.session_state.history[::-1]:
            st.markdown(
                f"<span style='font-size:1.2em; font-weight:600; color:#ffffff;'>{entry['title']}</span>",
                unsafe_allow_html=True
            )
            with st.expander("Preview"):
                st.write(entry['text'][:800] + ("..." if len(entry['text']) > 800 else ""))
            st.markdown("---")
    else:
        st.info("No papers uploaded or fetched yet.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "Settings":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"⚙️ {lang_dict[language]['settings']}")
    st.markdown("Select your preferred language, adjust accessibility options, or reset session.")
    font_size = st.slider("Font Size for Extracted Text", 12, 24, 16)
    st.markdown(f"<style>.stTextArea textarea {{ font-size: {font_size}px !important; }}</style>", unsafe_allow_html=True)
    if st.button("Reset All Session Data"):
        st.session_state.paper_text = ""
        st.session_state.paper_title = ""
        st.session_state.history = []
        st.success("Session reset! All papers and actions cleared.")
    st.markdown('</div>', unsafe_allow_html=True)