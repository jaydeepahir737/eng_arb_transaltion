# Offline AI English-Arabic Translator

A professional-grade, fully offline AI-powered bidirectional text translator designed for high-accuracy English-Arabic translation. Built with state-of-the-art open-source models, this tool handles documents of any length while maintaining contextual accuracy and grammatical correctness.

## 🚀 Key Features

- **Bidirectional Translation**: Seamless English ↔ Arabic translation
- **Document Processing**: Handles documents with thousands of words without truncation
- **Offline Operation**: Works completely offline after initial model download
- **Open Source Stack**: Built entirely with free, open-source libraries
- **Smart Text Processing**: Intelligent chunking preserves document structure and meaning
- **Automatic Language Detection**: Detects input language automatically
- **Web Interface**: Modern Streamlit UI for easy document upload and translation
- **Command Line Interface**: CLI tool for batch processing and automation

## 📋 System Requirements

### Hardware Requirements
- **Processor**: Intel i5 or equivalent (Intel i5 10th gen or newer recommended)
- **Memory**: 8GB RAM minimum (16GB recommended for large documents)
- **Storage**: 5GB free space for models and dependencies
- **Graphics**: CPU-only operation (GPU optional for acceleration)

### Software Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Internet**: Required only for initial model download (~2-3GB)

## 🛠 Installation Guide

### Step 1: Environment Setup

First, ensure you have Python 3.8+ installed on your system:

```bash
# Check Python version
python --version

# If Python is not installed, download from https://python.org
```


### Step 2: Virtual Environment (Recommended)

Create a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

Install the required Python packages:

```bash
# Install all dependencies
pip install -r requirements.txt
```

**Note**: This will install the following key libraries:
- `transformers==4.35.0`: HuggingFace Transformers for AI models
- `torch==2.1.0`: PyTorch for deep learning operations
- `streamlit==1.34.0`: Web interface framework
- `PyPDF2==3.0.1`: PDF text extraction
- `sentencepiece==0.1.99`: Text tokenization
- `sacremoses==0.0.53`: Text preprocessing
- `tqdm==4.66.1`: Progress bars
- `numpy==1.24.3`: Numerical computations

### Step : Model Download

The AI models will be automatically downloaded on first use:

This project utilizes pre-trained machine translation models from the Helsinki-NLP group, powered by the OPUS-MT framework:

English to Arabic: Helsinki-NLP/opus-mt-en-ar
Arabic to English: Helsinki-NLP/opus-mt-ar-en


**Important**: Ensure you have a stable internet connection for the initial model download.

## 🎯 Usage Instructions

### Web Interface (Recommended)

Launch the Streamlit web interface for the best user experience:

```bash or terminal
streamlit run streamlit_app.py
```

**Features**:
- Upload PDF files or paste text directly
- Real-time streaming translation display
- Side-by-side original and translated text
- Automatic language detection
- Progress tracking during translation

#### Running Streamlit on Other Devices

To access the translator from other devices on your network:

```bash
# Run Streamlit with network access
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

- **Local url**: `http://localhost:8501`


## 📝 Example Usage

### Web Interface Example
1. Run `streamlit run streamlit_app.py`
2. Open browser to the provided URL
3. Upload a PDF or paste text (You can take files in 'sample_files' folder with txt and pdfs.)
4. Select translation direction (or use auto-detect)
5. Click "Translate" and watch real-time results

