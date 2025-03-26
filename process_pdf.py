import google.generativeai as genai
import pdfplumber
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini AI
genai.configure(api_key="AIzaSyCUd4ZMonA-qcB_1sLu0gNgj_VYXkbQo1g")

# Configure the model settings
generation_config = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Different prompts for each option
PROMPTS = {
    "bullet": """
    Convert this text into clear, organized bullet points:
    - Extract the main concepts and key ideas
    - Highlight important definitions and terms
    - Create a hierarchical structure of topics
    - Include relevant examples or applications
    - Note any important relationships between concepts
    
    Text: {text}
    """,
    
    "paragraph": """
    Transform this text into well-structured study notes:
    - Organize the information into clear, logical paragraphs
    - Emphasize key concepts and their relationships
    - Include relevant examples and applications
    - Maintain a clear flow of ideas
    - Highlight important terms and definitions
    
    Text: {text}
    """,
    
    "time": """
    Create a chronological study guide from this text:
    - Organize concepts in a logical learning sequence
    - Start with foundational concepts
    - Build up to more complex ideas
    - Include prerequisites for each topic
    - Note dependencies between concepts
    - Suggest a learning timeline
    
    Text: {text}
    """
}

def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return None

def get_gemini_response(prompt, text):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.0-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Log available models for debugging
        try:
            available_models = [m.name for m in genai.list_models()]
            logger.info(f"Available models: {available_models}")
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            
        formatted_prompt = prompt.format(text=text)
        
        # Add safety check for text length
        if len(formatted_prompt) > 30000:
            text = text[:30000] + "..."
            formatted_prompt = prompt.format(text=text)
            
        response = model.generate_content(formatted_prompt)
        return response.text if response and hasattr(response, 'text') else None
    except Exception as e:
        logger.error(f"Error getting Gemini response: {str(e)}")
        return f"Error processing document: {str(e)}"

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        option = request.form.get('option', 'bullet')  # Default to bullet if no option provided
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Extract text from PDF
        text = extract_text_from_pdf(file)
        if not text:
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        # Get the appropriate prompt
        prompt = PROMPTS.get(option)
        if not prompt:
            return jsonify({'error': 'Invalid option'}), 400
        
        # Get response from Gemini
        response = get_gemini_response(prompt, text)
        if not response:
            return jsonify({'error': 'Could not process text. Please try again.'}), 500
        
        return jsonify({'response': response})
    
    except Exception as e:
        logger.error(f"Error in process_pdf endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 