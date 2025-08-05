import streamlit as st
import os
import tempfile
from translate import OfflineTranslator
import PyPDF2
import time

st.set_page_config(page_title="English-Arabic PDF Translator", layout="wide")
st.title("📄 English ↔ Arabic PDF Translator (Offline AI)")
st.write("Upload a PDF or paste text in English or Arabic. The translation will appear side-by-side, line by line.")

translator = OfflineTranslator()

def extract_pdf_lines(pdf_file) -> list:
    lines = []
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                page_lines = text.splitlines()
                lines.extend(page_lines)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return lines

def translate_lines_streaming(lines, direction=None):
    """Translate lines with streaming output."""
    translated = []
    for i, line in enumerate(lines):
        if line.strip():
            translated_line = translator.translate_text(line, direction)
        else:
            translated_line = ""
        translated.append(translated_line)
        yield translated, i + 1, len(lines)  # Return current progress

def count_words(lines):
    return sum(len(line.split()) for line in lines if line.strip())

# --- UI ---

language = st.selectbox("Translation direction", ["Auto-detect", "English → Arabic", "Arabic → English"])
option = st.radio("Choose input method:", ["Upload PDF", "Paste Text"], horizontal=True)

lines = []
input_label = "Paste your text here (English or Arabic, one paragraph per line):"

if option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_pdf_path = tmp_file.name
        st.info("Extracting text from PDF...")
        lines = extract_pdf_lines(tmp_pdf_path)
        os.remove(tmp_pdf_path)
        if lines:
            if st.button("Translate PDF", key="translate_pdf_btn"):
                start_time = time.time()
                
                # Create placeholders for streaming output
                progress_bar = st.progress(0)
                status_text = st.empty()
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Original Text")
                    # Create empty container for original text
                    orig_container = st.empty()
                with col2:
                    st.subheader("Translation")
                    # Create empty container for translated text
                    trans_container = st.empty()
                
                # Set direction
                if language == "English → Arabic":
                    direction = "en2ar"
                elif language == "Arabic → English":
                    direction = "ar2en"
                else:
                    direction = None
                
                # Stream translations
                orig_full_text = ""
                trans_full_text = ""
                
                for translated_lines, current, total in translate_lines_streaming(lines, direction):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"Translating... {current}/{total} lines ({progress:.1%})")
                    
                    # Build the full text as we go
                    if current <= len(lines):
                        orig_full_text += lines[current-1] + "\n"
                        if current <= len(translated_lines) and translated_lines[current-1]:
                            trans_full_text += translated_lines[current-1] + "\n"
                        
                        # Update the containers with current content
                        with orig_container:
                            st.text_area("Original", value=orig_full_text, height=500, disabled=False, key=f"orig_{current}")
                        with trans_container:
                            st.text_area("Translation", value=trans_full_text, height=500, disabled=False, key=f"trans_{current}")
                
                elapsed = time.time() - start_time
                orig_word_count = count_words(lines)
                trans_word_count = count_words(translated_lines)
                
                progress_bar.empty()
                status_text.empty()
                st.success(f"Translation complete! | Original words: {orig_word_count} | Translated words: {trans_word_count} | Time taken: {elapsed:.2f} seconds")
                
elif option == "Paste Text":
    pasted_text = st.text_area(input_label, height=200)
    if pasted_text:
        lines = pasted_text.splitlines()
        if st.button("Translate Text", key="translate_text_btn"):
            start_time = time.time()
            
            # Create placeholders for streaming output
            progress_bar = st.progress(0)
            status_text = st.empty()
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original Text")
                # Create empty container for original text
                orig_container = st.empty()
            with col2:
                st.subheader("Translation")
                # Create empty container for translated text
                trans_container = st.empty()
            
            # Set direction
            if language == "English → Arabic":
                direction = "en2ar"
            elif language == "Arabic → English":
                direction = "ar2en"
            else:
                direction = None
            
            # Stream translations
            orig_full_text = ""
            trans_full_text = ""
            
            for translated_lines, current, total in translate_lines_streaming(lines, direction):
                progress = current / total
                progress_bar.progress(progress)
                status_text.text(f"Translating... {current}/{total} lines ({progress:.1%})")
                
                # Build the full text as we go
                if current <= len(lines):
                    orig_full_text += lines[current-1] + "\n"
                    if current <= len(translated_lines) and translated_lines[current-1]:
                        trans_full_text += translated_lines[current-1] + "\n"
                    
                    # Update the containers with current content
                    with orig_container:
                        st.text_area("Original", value=orig_full_text, height=500, disabled=False, key=f"orig_paste_{current}")
                    with trans_container:
                        st.text_area("Translation", value=trans_full_text, height=500, disabled=False, key=f"trans_paste_{current}")
            
            elapsed = time.time() - start_time
            orig_word_count = count_words(lines)
            trans_word_count = count_words(translated_lines)
            
            progress_bar.empty()
            status_text.empty()
            st.success(f"Translation complete! | Original words: {orig_word_count} | Translated words: {trans_word_count} | Time taken: {elapsed:.2f} seconds") 