from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import pdfplumber
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure Gemini AI with safety settings
GOOGLE_API_KEY = "AIzaSyDyroizCws1r7wVTMLxOWt81_mHJ-4qxAE"
genai.configure(api_key=GOOGLE_API_KEY)

# Set the API version explicitly
os.environ['GOOGLE_API_VERSION'] = 'v1beta'

# Configure the model with safety settings
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

def process_text(text, format_type):
    try:
        if not text or len(text.strip()) == 0:
            logger.error("Empty text provided to process_text")
            return None

        # Initialize the model with configurations
        try:
            # Create the model with explicit version
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Log model details for debugging
            logger.info("Model initialization successful")
            logger.info(f"Using model: gemini-2.0-flash")
            logger.info(f"API Version: {os.getenv('GOOGLE_API_VERSION', 'Not set')}")
            
            # Create the prompt
            prompts = {
                'bullet': """
                Convert this text into clear, organized bullet points:
                - Extract the main concepts and key ideas
                - Highlight important definitions and terms
                - Create a hierarchical structure of topics
                - Include relevant examples or applications
                - Note any important relationships between concepts

                Text: {text}
                """,
                
                'paragraph': """
                Transform this text into well-structured study notes:
                - Organize the information into clear, logical paragraphs
                - Emphasize key concepts and their relationships
                - Include relevant examples and applications
                - Maintain a clear flow of ideas
                - Highlight important terms and definitions

                Text: {text}
                """,
                
                'time': """
                Create a detailed study time schedule from this text:
                - Break down the content into manageable study sessions
                - Suggest specific time durations for each topic
                - Include recommended breaks and rest periods
                - Consider topic complexity when allocating time
                - Recommend daily and weekly study hours
                - Include tips for maintaining focus during each session
                - Suggest review periods and revision schedules

                Text: {text}
                """
            }
            
            prompt = prompts.get(format_type, prompts['bullet']).format(text=text)
            
            # Add safety check for text length
            if len(prompt) > 30000:
                text = text[:30000] + "..."
                prompt = prompts.get(format_type, prompts['bullet']).format(text=text)
            
            # Generate content with proper response handling
            try:
                response = model.generate_content(prompt)
                logger.info("Content generation successful")
                
                if response and hasattr(response, 'text'):
                    logger.info("Using response.text format")
                    return response.text
                elif response and hasattr(response, 'parts'):
                    logger.info("Using response.parts format")
                    text_content = ' '.join([part.text for part in response.parts])
                    return text_content
                else:
                    logger.error("Response format not recognized")
                    return None
                    
            except Exception as gen_error:
                logger.error(f"Content generation error: {str(gen_error)}")
                return f"Error generating content: {str(gen_error)}"
                
        except Exception as model_error:
            logger.error(f"Model initialization error: {str(model_error)}")
            return f"Error initializing model: {str(model_error)}"
            
    except Exception as e:
        logger.error(f"General error in process_text: {str(e)}")
        return str(e)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        format_type = request.form.get('option', 'bullet')
        if format_type not in ['bullet', 'paragraph', 'time']:
            return jsonify({'error': 'Invalid format type'}), 400
        
        # Extract text from PDF
        text = extract_text_from_pdf(file)
        if not text:
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        # Process the text
        result = process_text(text, format_type)
        if not result:
            return jsonify({'error': 'Could not process text. Please try again.'}), 500
        
        return jsonify({'response': result})
    except Exception as e:
        logger.error(f"Error in process_pdf endpoint: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
