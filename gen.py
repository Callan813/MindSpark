import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Set the API version explicitly
os.environ['GOOGLE_API_VERSION'] = 'v1beta'

# Configure Generative AI with API key
GOOGLE_API_KEY = "AIzaSyDyroizCws1r7wVTMLxOWt81_mHJ-4qxAE"
genai.configure(api_key=GOOGLE_API_KEY)

# Log configuration details
logging.info("Initializing Gemini configuration...")
logging.info(f"API Version: {os.getenv('GOOGLE_API_VERSION', 'Not set')}")

# Model configuration
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

# Initialize the model
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    logging.info("Successfully initialized Gemini model")
    logging.info("Using model: gemini-2.0-flash")
except Exception as e:
    logging.error(f"Failed to initialize model: {str(e)}")
    raise Exception(f"Failed to initialize Gemini model: {str(e)}")

# Function to extract text from uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

# Function to clean JSON array elements by ensuring they are quoted
def clean_json_array(response):
    # Find all arrays in the JSON string using regex
    def clean_array(match):
        array_str = match.group(0)  # Full array string, e.g., '[item1, "item2", item3]'
        # Extract elements by splitting on commas, preserving quoted strings
        elements = re.split(r',\s*(?=(?:[^"]"[^"]")[^"]$)', array_str[1:-1])  # Remove [ and ]
        cleaned_elements = []
        for elem in elements:
            elem = elem.strip()
            if elem and not (elem.startswith('"') and elem.endswith('"')):
                # Add quotes if not already quoted
                elem = f'"{elem}"'
            cleaned_elements.append(elem)
        return f'[{",".join(cleaned_elements)}]'
    
    # Replace all arrays with cleaned versions
    cleaned_response = re.sub(r'\[.*?\]', clean_array, response, flags=re.DOTALL)
    return cleaned_response

# Enhanced function to ensure valid JSON
def ensure_valid_json(response):
    """More robust JSON cleaning function"""
    try:
        # First try direct JSON parsing
        json.loads(response)
        return response
    except json.JSONDecodeError:
        # If direct parsing fails, try cleaning and fixing the response
        try:
            # Clean the response
            cleaned = clean_json_array(response)
            
            # Basic check - ensure response starts with { and ends with }
            cleaned = cleaned.strip()
            if not cleaned.startswith('{'):
                start_idx = cleaned.find('{')
                if (start_idx != -1):
                    cleaned = cleaned[start_idx:]
                else:
                    cleaned = '{' + cleaned
            
            if not cleaned.endswith('}'):
                end_idx = cleaned.rfind('}')
                if end_idx != -1:
                    cleaned = cleaned[:end_idx+1]
                else:
                    cleaned = cleaned + '}'
            
            # Validate the JSON
            json.loads(cleaned)
            return cleaned
        except:
            # If all cleaning attempts fail, create a simple valid JSON
            logging.error("Failed to parse or fix JSON, creating simple format")
            simple_json = {
                "Document Type": "Document Analysis",
                "Key Details": {"Note": "Structured data unavailable"},
                "Summary": response[:500] + "..." if len(response) > 500 else response,
                "Tips": "Please try again with a clearer document.",
                "Hidden Clauses": "No hidden clauses detected.",
                "Guesses": []
            }
            return json.dumps(simple_json)

# Function to get Gemini response
def get_gemini_response(prompt):
    try:
        # Initialize model with configurations
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        logging.info("Model initialized successfully")
        logging.info("Using model: gemini-2.0-flash")
        
        try:
            # Generate content
            response = model.generate_content(prompt)
            logging.info("Content generation successful")
            
            # Handle different response formats
            if response and hasattr(response, 'text'):
                logging.info("Using response.text format")
                return response.text
            elif response and hasattr(response, 'parts'):
                logging.info("Using response.parts format")
                text_content = ' '.join([part.text for part in response.parts])
                return text_content
            else:
                logging.error("Invalid response format from Gemini API")
                return "Error: Could not process response"
        except Exception as gen_error:
            logging.error(f"Content generation error: {str(gen_error)}")
            return f"Error generating content: {str(gen_error)}"
    except Exception as e:
        logging.error(f"Model initialization error: {str(e)}")
        return str(e)

# Updated Prompt Template for Simplified Financial Document Analysis
input_prompt = """
Act as a friendly financial guide who explains things in simple, everyday language—like you're helping a friend. 
Your job is to analyze the uploaded financial document (e.g., loan agreement, passbook, bank statement) and pull out key details like loan amount, interest rate, repayment time, or monthly payments—whatever fits the document. 

Break down any confusing financial terms (e.g., "EMI" means "monthly payment") and highlight hidden clauses or tricky parts (e.g., penalties, extra fees, or rate changes) that might catch someone off guard. Give a clear summary and practical tips—like how to save money or avoid trouble—without using jargon. If details are missing, guess sensibly and say so. Suggest a chart if it helps explain things visually.

Document Text: {document_text}

The response structure should be:
{{
   "Document Type": "e.g., Loan Agreement, Passbook, Bank Statement",
   "Key Details": {{"key1": "value1 (simple explanation)", "key2": "value2 (simple explanation)", ...}},
   "Summary": "short, easy summary",
   "Tips": "practical, friendly advice",
   "Hidden Clauses": "Write all hidden clauses as one coherent paragraph instead of a list. Explain all the tricky parts of the document that readers should be aware of.",
   "Guesses": ["guess1", "guess2", ...]
}}
"""

# Apply custom CSS with React-matching gradient and elements
st.markdown("""
<style>
/* Global text color settings */
.main * {
    color: #FFFFFF !important; /* Make all text white by default */
}

/* Apply the new gradient from #300654 to white */
.stApp {
    background: linear-gradient(to bottom, #300654, #7521b5);
}

/* Header styling */
.gradient-header {
    padding: 1.5rem;
    margin-bottom: 2rem;
    text-align: center;
}

.gradient-header h1 {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 1rem;
    color: #FFFFFF !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.gradient-header p {
    font-size: 1.25rem;
    max-width: 700px;
    margin: 0 auto;
    color: #FFFFFF !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* White content panels with white text */
.content-panel {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 1.5rem;
    border-radius: 1rem;
    margin: 1.5rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    transition: transform 0.3s, box-shadow 0.3s;
}

.content-panel:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

/* Larger, more prominent section headers */
.section-header {
    color: #FFFFFF !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    margin-bottom: 1.5rem;
    text-align: center;
    border-bottom: 2px solid #FFFFFF;
    padding-bottom: 0.5rem;
}

/* Detail items styled with brand color accents */
.detail-item {
    margin-bottom: 1rem;
    padding: 1rem;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 0.5rem;
    border-left: 4px solid #FFFFFF;
}

.detail-item strong {
    color: #FFFFFF !important;
    font-weight: 700;
    font-size: 1.2rem;
    display: block;
    margin-bottom: 0.5rem;
}

/* Ensure all text content in panels is white */
.content-panel p, 
.content-panel div, 
.content-panel span {
    color: white !important;
}

/* Warning panel with contrasting colors */
.warning-panel {
    background-color: rgba(238, 130, 238, 0.1);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin: 1.5rem 0;
    border-left: 6px solid #EE82EE;
}

.warning-panel p,
.warning-panel .section-header {
    color: #FFFFFF !important;
}

.warning-panel .section-header {
    border-bottom-color: #EE82EE;
}

/* Tips panel with brand colors */
.tips-panel {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin: 1.5rem 0;
    border-left: 6px solid #FFFFFF;
}

.tips-panel p,
.tips-panel .section-header {
    color: #FFFFFF !important;
}

/* Document type header */
.doc-type {
    background-color: rgba(255, 255, 255, 0.15);
    color: white !important;
    padding: 1.2rem;
    border-radius: 0.75rem;
    text-align: center;
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 2rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

/* Button styling */
.stButton > button {
    display: inline-flex;
    align-items: center;
    background-color: #151212FF;
    color: #000000 !important;
    padding: 1rem 2rem;
    border-radius: 0.5rem;
    font-size: 1.2rem;
    font-weight: 700;
    text-decoration: none;
    transition: transform 0.3s, background-color 0.3s;
    border: none !important;
}

.stButton > button:hover {
    background-color: #f0f0f0;
    transform: scale(1.05);
}

/* File uploader styling */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1.5rem;
}

/* Status message styling */
.stSuccess, .stInfo {
    background-color: rgba(209, 250, 229, 0.3) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 0.5rem;
}

.stError, .stWarning {
    background-color: rgba(255, 75, 75, 0.2) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 0.5rem;
}

/* Guess items matching brand style */
.guess-item {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    color: #FFFFFF !important;
    border-left: 4px solid #FFFFFF;
}

/* Floating animation for spinner */
.stSpinner {
    animation: float 2s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

/* Ensure expanders match the theme */
.streamlit-expanderHeader {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
    border-radius: 0.5rem;
}

/* Style code blocks and technical details */
pre {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #FFFFFF;
}

/* Make label text white */
label {
    color: #FFFFFF !important;
}

/* Fix any remaining dark text */
p, h1, h2, h3, h4, h5, span, div {
    color: #FFFFFF !important;
}

/* Improve contrast for links */
a {
    color: #FFCF4D !important;
    text-decoration: underline;
}
</style>
    """, unsafe_allow_html=True)

# App title and description styled like React app
st.markdown("<div class=\"gradient-header\"><h1>FinAI Document Helper</h1><p>Upload a loan paper, passbook, or bank statement—I'll explain it simply and spot any sneaky stuff!</p></div>", unsafe_allow_html=True)

# Document upload
uploaded_file = st.file_uploader("Upload Your Document (PDF)", type="pdf", help="Drop a loan agreement, passbook, or any money-related PDF here.")

# Submit button styled like React
submit = st.button("Analyze Document")

# On submit action
if submit:
    if uploaded_file is not None:
        # Show a loading spinner with a friendly message
        with st.spinner("Taking a look at your document..."):
            try:
                # Extract text from uploaded PDF
                text = input_pdf_text(uploaded_file)
                
                # Prepare the prompt with document text
                prompt = input_prompt.format(document_text=text)
                
                # Get response from Gemini API
                response = get_gemini_response(prompt)
                logging.info(f"API Response: {response}")

                # Clean the JSON response to ensure valid formatting
                cleaned_response = ensure_valid_json(response)
                logging.info(f"Cleaned Response: {cleaned_response}")

                # Parse the response
                try:
                    response_data = json.loads(cleaned_response)
                    doc_type = response_data.get("Document Type", "Not Sure").strip()
                    key_details = response_data.get("Key Details", {})
                    summary = response_data.get("Summary", "No summary yet.").strip()
                    tips = response_data.get("Tips", "No tips yet.").strip()
                    hidden_clauses = response_data.get("Hidden Clauses", "No hidden clauses detected.")
                    guesses = response_data.get("Guesses", [])

                    if not isinstance(key_details, dict):
                        st.error("The Key Details section is not in the expected format.")
                        st.stop()
                    
                    # Clean key_details keys by removing leading/trailing spaces
                    key_details = {k.strip(): v.strip() for k, v in key_details.items()}

                    # Display results in a friendly, clear way
                    st.success("Analysis Complete")
                    
                    # Display document type
                    st.markdown(f"<div class='doc-type'>{doc_type}</div>", unsafe_allow_html=True)
                    
                    # Display key details with explanations
                    st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-header'>Key Details</div>", unsafe_allow_html=True)
                    if key_details:
                        for key, value in key_details.items():
                            st.markdown(f"<div class='detail-item'><strong>{key}:</strong> {value}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p>Couldn't find any key details in this document.</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Display summary
                    st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-header'>Summary</div>", unsafe_allow_html=True)
                    st.markdown(f"<p>{summary}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Display tips
                    st.markdown("<div class='content-panel tips-panel'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-header'>Financial Tips</div>", unsafe_allow_html=True)
                    st.markdown(f"<p>{tips}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Display hidden clauses as paragraph
                    st.markdown("<div class='content-panel warning-panel'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-header'>Hidden Clauses & Watch-Outs</div>", unsafe_allow_html=True)
                    st.markdown(f"<p>{hidden_clauses}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Display guesses
                    if guesses:
                        st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-header'>Estimated Information</div>", unsafe_allow_html=True)
                        for guess in guesses:
                            st.markdown(f"<div class='guess-item'>{guess.strip()}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                
                except json.JSONDecodeError as e:
                    logging.error(f"JSON Decode Error: {cleaned_response}, Error: {e}")
                    st.error(f"Oops! There was an issue analyzing your document. Please try again. (Error: {str(e)[:100]}...)")
                    # Show raw response for debugging
                    with st.expander("Technical Details"):
                        st.code(response[:1000] + "..." if len(response) > 1000 else response)
                except KeyError as e:
                    logging.error(f"Missing key in AI response: {e}. Response: {cleaned_response}")
                    st.error(f"Missing information in the analysis. Please try again. Error: {e}")
                    # Show raw response for debugging
                    with st.expander("Technical Details"):
                        st.code(response[:1000] + "..." if len(response) > 1000 else response)
            
            except Exception as e:
                logging.error(f"General error: {str(e)}")
                st.error(f"Something went wrong: {str(e)}")

    else:
        st.warning("Please upload a document to analyze.")