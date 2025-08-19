# English-Arabic Offline Translator API

A professional-grade, fully offline REST API for high-accuracy, bidirectional English-Arabic translation. Built with state-of-the-art open-source models, this service handles long documents and text streams while maintaining contextual accuracy.

## 🚀 Key Features

-   **REST API Endpoints**: Simple and powerful endpoints for text and PDF translation.
-   **Asynchronous PDF Processing**: Submitting large PDFs returns a task ID immediately, preventing client timeouts.
-   **Bidirectional Translation**: Seamless English ↔ Arabic translation.
-   **Handles Large Documents**: Translates documents with thousands of words without truncation.
-   **Offline Operation**: Works completely offline after the initial model download.
-   **Automatic Language Detection**: Detects the input language automatically.

---
## 📋 System Requirements

### Hardware
-   **Processor**: Intel i5 or equivalent (Intel i5 10th gen or newer recommended)
-   **Memory**: 8GB RAM minimum (16GB recommended for large documents)
-   **Storage**: 5GB free space for models and dependencies

### Software
-   **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
-   **Python**: Version 3.8 or higher
-   **Internet**: Required only for the initial model download (~2-3GB).

---
## 🛠 Installation Guide

This project requires a specific version of PyTorch that matches your hardware. Please follow these steps carefully.

### Step 1: Install PyTorch
First, install PyTorch separately. Go to the **[official PyTorch website](https://pytorch.org/get-started/locally/)**, select the correct options for your system (e.g., Windows, Pip, CPU or CUDA), and run the command they provide. This ensures maximum compatibility and performance.

### Step 2: Clone and Install Project Dependencies
Once PyTorch is installed, you can set up the project and install the rest of the required packages.

```bash
# Clone the repository
git clone [https://github.com/jaydeepahir737/eng_arb_transaltion.git](https://github.com/jaydeepahir737/eng_arb_transaltion.git)
cd eng_arb_transaltion

# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install the remaining dependencies
pip install -r requirements.txt

🎯 Running the API
Once installation is complete, start the Flask server from the project's root directory:

Bash

python main.py

The API will be live and listening for requests at http://127.0.0.1:5000.

📝 API Endpoints
1. Translate Plain Text
Endpoint: POST /translate/text

Description: Translates a block of text synchronously. Best for short-to-medium length text.

Request Body (application/json):

JSON

{
    "text": "Hello world.\nThis is a new line.",
    "direction": "en2ar"
}
Success Response (200 OK):

JSON

{
    "original_lines": [ "Hello world.", "This is a new line." ],
    "translated_lines": [ "مرحبا بالعالم.", "هذا خط جديد." ],
    "word_count_original": 6,
    "word_count_translated": 5
}
2. Translate a PDF (Asynchronous)
Step A: Start the Translation Job
Endpoint: POST /translate/pdf

Description: Accepts a PDF file, starts a background translation job, and returns a task ID immediately.

Request Body (multipart/form-data):

file: The PDF file to be translated.

direction: (Optional) en2ar or ar2en.

Success Response (202 Accepted):

JSON

{
    "message": "Translation started.",
    "task_id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
    "status_url": "/status/a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
}
Step B: Check Job Status
Endpoint: GET /status/<task_id>

Description: Retrieves the status and result of a translation job.

Success Response (200 OK):

JSON

{
    "task_id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
    "status": "completed",
    "result": {
        "original_lines": [ "Text from PDF..." ],
        "translated_lines": [ "النص المترجم من PDF..." ],
        "word_count_original": 3,
        "word_count_translated": 4,
        "output_file": "translated_files\\your_document_translated.txt"
    }
}
💡 Example Usage (curl)
Translate Text
Bash

curl -X POST \
  http://127.0.0.1:5000/translate/text \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "This is a test.",
    "direction": "en2ar"
  }'
Translate a PDF
Bash

# Step 1: Upload the PDF and get a task_id
curl -X POST \
  http://127.0.0.1:5000/translate/pdf \
  -F 'file=@/path/to/your/document.pdf' \
  -F 'direction=en2ar'

# Step 2: Use the task_id from the response to check the status
curl http://127.0.0.1:5000/status/<your_task_id_here>






