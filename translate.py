#!/usr/bin/env python3
"""
Offline AI-Based English-Arabic Bidirectional Text Translator
Supports very long documents with efficient chunking and reassembly.
"""

import argparse
import os
import sys
from typing import List, Tuple
import torch
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm
import re
import PyPDF2

# Set a custom HuggingFace cache directory
os.environ["HF_HOME"] = os.path.abspath("hf_cache")

class OfflineTranslator:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
    def load_model(self, direction: str):
        """Load the appropriate model for the translation direction."""
        if direction in self.models:
            return self.models[direction], self.tokenizers[direction]
        
        # Model mapping for different translation directions
        model_mapping = {
            'en2ar': 'Helsinki-NLP/opus-mt-en-ar',
            'ar2en': 'Helsinki-NLP/opus-mt-ar-en'
        }
        
        model_name = model_mapping.get(direction)
        if not model_name:
            raise ValueError(f"Unsupported translation direction: {direction}")
        
        print(f"Loading model: {model_name}")
        print("This may take a few minutes on first run...")
        
        try:
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            model.to(self.device)
            
            self.models[direction] = model
            self.tokenizers[direction] = tokenizer
            
            print(f"Model {direction} loaded successfully!")
            return model, tokenizer
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Make sure you have internet connection for initial model download.")
            sys.exit(1)
    
    def detect_language(self, text: str) -> str:
        """Simple language detection based on character sets."""
        arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', text))
        total_chars = len(re.sub(r'\s', '', text))
        
        if total_chars == 0:
            return 'en'  # Default to English
        
        arabic_ratio = arabic_chars / total_chars
        return 'ar' if arabic_ratio > 0.3 else 'en'
    
    def chunk_text(self, text: str, max_length: int = 512) -> List[str]:
        """Split long text into manageable chunks while preserving sentence boundaries."""
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed max_length, start a new chunk
            if len(current_chunk) + len(sentence) > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += ". " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    def translate_chunk(self, text: str, model, tokenizer) -> str:
        """Translate a single chunk of text."""
        if not text.strip():
            return ""
        
        # Tokenize
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate translation
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=512, num_beams=5, early_stopping=True)
        
        # Decode
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translation
    
    def translate_text(self, text: str, direction: str = None) -> str:
        """Translate text with automatic direction detection if not specified."""
        if not direction:
            detected_lang = self.detect_language(text)
            direction = 'ar2en' if detected_lang == 'ar' else 'en2ar'
            print(f"Detected language: {detected_lang}, using direction: {direction}")
        
        # Load model
        model, tokenizer = self.load_model(direction)
        
        # Chunk the text for long documents
        chunks = self.chunk_text(text)
        print(f"Processing {len(chunks)} chunks...")
        
        # Translate each chunk
        translations = []
        for i, chunk in enumerate(tqdm(chunks, desc="Translating")):
            if chunk.strip():
                translation = self.translate_chunk(chunk, model, tokenizer)
                translations.append(translation)
        
        # Reassemble the translated text
        return " ".join(translations)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF file."""
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
            sys.exit(1)
        return text
    
    def translate_file(self, input_file: str, output_file: str, direction: str = None):
        """Translate a file (txt or pdf) and save the result."""
        try:
            # Detect PDF or text file
            if input_file.lower().endswith('.pdf'):
                print(f"Detected PDF file: {input_file}")
                text = self.extract_text_from_pdf(input_file)
            else:
                with open(input_file, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            print(f"Input file: {input_file}")
            print(f"Text length: {len(text)} characters")
            
            # Translate
            translated_text = self.translate_text(text, direction)
            
            # Write output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            
            print(f"Translation saved to: {output_file}")
            print(f"Output length: {len(translated_text)} characters")
            
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error during translation: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Offline AI English-Arabic Translator')
    parser.add_argument('input', help='Input text or file path')
    parser.add_argument('output', help='Output file path (for file mode)')
    parser.add_argument('--lang', choices=['en2ar', 'ar2en'], 
                       help='Translation direction (auto-detected if not specified)')
    parser.add_argument('--text', action='store_true', 
                       help='Treat input as direct text instead of file path')
    
    args = parser.parse_args()
    
    translator = OfflineTranslator()
    
    if args.text:
        # Direct text translation
        translated = translator.translate_text(args.input, args.lang)
        print("\nTranslation:")
        print("-" * 50)
        print(translated)
        print("-" * 50)
    else:
        # File translation
        translator.translate_file(args.input, args.output, args.lang)

if __name__ == "__main__":
    main() 