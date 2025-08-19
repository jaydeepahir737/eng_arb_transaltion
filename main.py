import os
import tempfile
import uuid
import threading
from flask import Flask, request, jsonify

# --- Local Imports ---
import PyPDF2
from translate import OfflineTranslator

# --- Flask App Setup ---
app = Flask(__name__)

# --- In-memory storage for task status (for demonstration) ---
# In a real production app, you'd use a database or Redis for this.
tasks = {}

# --- Create a directory for saved translations ---
OUTPUT_DIR = "translated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- Translator Initialization ---
print("Initializing the translator...")
translator = OfflineTranslator()
print("Translator ready.")


# --- Helper Functions (mostly unchanged) ---
def extract_pdf_lines(pdf_file_path: str) -> list:
    lines = []
    try:
        with open(pdf_file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    lines.extend(text.splitlines())
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return []
    return lines

def translate_lines(lines: list, direction: str | None) -> list:
    return [
        translator.translate_text(line, direction=direction) if line.strip() else ""
        for line in lines
    ]

def count_words(lines: list) -> int:
    return sum(len(line.split()) for line in lines if line.strip())

# --- NEW: Background Task Function ---
def run_translation_task(task_id: str, pdf_path: str, original_filename: str, direction: str | None):
    """This function runs in a separate thread and performs the heavy lifting."""
    try:
        # Update status to 'processing'
        tasks[task_id]['status'] = 'processing'
        
        # 1. Extract text from PDF
        original_lines = extract_pdf_lines(pdf_path)
        if not original_lines:
            raise ValueError("Could not extract text from PDF.")
            
        # 2. Translate the text
        translated_lines = translate_lines(original_lines, direction)
        
        # 3. Save the translated output to a file
        output_filename = f"{os.path.splitext(original_filename)[0]}_translated.txt"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(translated_lines))
            
        # 4. Prepare the final result
        result = {
            "original_lines": original_lines,
            "translated_lines": translated_lines,
            "word_count_original": count_words(original_lines),
            "word_count_translated": count_words(translated_lines),
            "output_file": output_path
        }
        
        # Update task status to 'completed' with the result
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['result'] = result

    except Exception as e:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['error'] = str(e)
    finally:
        # Clean up the temporary PDF file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


# --- API Endpoints ---
@app.route("/translate/text", methods=['POST'])
def translate_text_endpoint():
    # This endpoint remains synchronous as it's usually fast.
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid request. 'text' key is required."}), 400
    original_lines = data['text'].splitlines()
    direction = data.get('direction')
    translated_lines = translate_lines(original_lines, direction)
    response = {
        "original_lines": original_lines,
        "translated_lines": translated_lines,
        "word_count_original": count_words(original_lines),
        "word_count_translated": count_words(translated_lines),
    }
    return jsonify(response)


@app.route("/translate/pdf", methods=['POST'])
def translate_pdf_endpoint_async():
    """
    MODIFIED: This endpoint now starts a background job and returns immediately.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        file.save(tmp_file)
        tmp_pdf_path = tmp_file.name

    # Create a unique ID for this task
    task_id = str(uuid.uuid4())
    direction = request.form.get('direction')
    
    # Store initial task info
    tasks[task_id] = {'status': 'pending'}
    
    # Start the translation in a background thread
    thread = threading.Thread(
        target=run_translation_task,
        args=(task_id, tmp_pdf_path, file.filename, direction)
    )
    thread.start()
    
    # Immediately return a response to the client
    return jsonify({
        "message": "Translation started.",
        "task_id": task_id,
        "status_url": f"/status/{task_id}"
    }), 202 # HTTP 202 Accepted status


@app.route("/status/<task_id>", methods=['GET'])
def get_status(task_id):
    """
    NEW: This endpoint lets you check the status of a background job.
    """
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404
        
    response = {"task_id": task_id, "status": task.get('status')}
    
    if task.get('status') == 'completed':
        response['result'] = task.get('result')
    elif task.get('status') == 'failed':
        response['error'] = task.get('error')
        
    return jsonify(response)


# --- To run the app directly ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)