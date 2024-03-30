import streamlit as st
import os
import base64
import google.generativeai as genai
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Set up Google API key
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")

# Configure generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Function to load OpenAI model and get responses
def get_gemini_response(input_text, image, prompt):
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        }
    ]

    model = genai.GenerativeModel("gemini-pro-vision")
    # model = model.start_chat(history=[])
    response = model.generate_content([input_text, image[0], prompt],safety_settings=safety_settings)
    # print(response)
    
    # return response.text

     # Check if the response contains any safety ratings
    if hasattr(response, 'safety_ratings') and response.safety_ratings:
        raise ValueError("The response was blocked due to safety concerns. Please try again with different input.")
    
    
    # Check if the response contains a valid Part
    if response.parts:
        return response.parts[0].text
    else:
        raise ValueError("The response does not contain a valid Part. Please try again.")


def input_image_setup(uploaded_image):
    if uploaded_image is not None:
        bytes_data = uploaded_image.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_image.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        st.error("Can't read uploaded image.")


# Initialize Streamlit app
st.set_page_config(page_title="Brainy AI",
                   page_icon="🤔",
                   layout="centered",
                   initial_sidebar_state="expanded")

# Custom CSS for gradient background and centering content
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #ff7e5f, #feb47b); /* Gradient from pink to orange */
        font-family: Arial, sans-serif;
    }
    .container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    .title {
        color: #fff; /* White color */
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center; /* Center the text */
    }
    .subtitle {
        color: #fff; /* White color */
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center; /* Center the text */
    }
    </style>
    """, unsafe_allow_html=True)

# Main content
# Main content
with st.container() as container:
    with st.container() as content:
        # Updated title
        st.markdown("# Brainy AI")
        st.markdown("### Extracting and Solving Questions from Documents")


# Sidebar
# Revised sidebar content
st.sidebar.header("Brainy AI")

with st.sidebar:
    st.image("pic.png", use_column_width=True)  # Add your logo here for branding
    st.markdown(
        """
        ## Welcome to Brainy AI
        Effortlessly extract insights from academic documents. Our AI solution streamlines analysis, empowering researchers 
        and educators with precise summaries for informed decision-making.
        """
    )



# Separator with improved styling
st.markdown(
    """
    <style>
    .separator {
        margin-top: 20px;
        margin-bottom: 20px;
        height: 3px;
        background-color: #ddd;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='separator'></div>", unsafe_allow_html=True)


# Input area
input_text = st.text_input(
    label="Enter key terms and details to generate a descriptive document summary:",
    placeholder="Provide details for document summarization...",
    key="document_input",
    help="Please enter relevant information and key terms to generate a detailed document summary."
)

# Image uploader
uploaded_image = st.file_uploader("Select an image...",
                                  type=["jpg", "jpeg", "png"],
                                  help=r"Click the `Browse files` to upload an image of your choice.")

# Display uploaded image
if uploaded_image is not None:
    image_data = base64.b64encode(uploaded_image.read()).decode()
    st.markdown(
        f'<div style="display: flex; justify-content: center;"><img src="data:image/png;base64,{image_data}" '
        f'alt="Uploaded Image" style="width: 50%; height: auto; max-width: 500px; border-radius: 15%; '
        f'border: 10px solid #ff7f0e;"></div>',
        unsafe_allow_html=True
    )

# Button to trigger description generation
submit_button = st.button("Show Solutions")

# Predefined prompt
input_prompt = """
    Welcome to the Brainy AI for academic purposes.

    Your expertise is crucial in accurately extracting questions from documents across different subjects and providing detailed solutions or explanations.
    
    Your task involves analyzing the provided document and identifying questions along with their relevant context and details.
    
    Example: Identify and extract questions from the document covering various subjects such as mathematics, science, literature, history, etc. Provide detailed explanations or solutions for each question.
    
    Think before solving and don't say a random answer.always be sure of your answer
    
    Your goal is to create a comprehensive list of questions covering a wide range of topics present in the document. 
    
    Maintain clarity and precision in your extraction process to ensure the accuracy of the questions and solutions provided.
     
    Feel free to ask if you need further clarification on any concept or question type.
    
    display your answers in a professional format like the following:
    
        Question:
        
        Solution:
     
    
    Happy extracting!

   """

# Handle button click event
if submit_button:
    if uploaded_image and input_text:
        with st.spinner("Reading your Questions and generating Solutions..."):
            start = time.time()
            image_data = input_image_setup(uploaded_image)
            response = get_gemini_response(input_text, image_data, input_prompt)
            st.subheader("HELLO \n Here is the solution:")
            st.markdown(response)
            end = time.time()
    elif uploaded_image and not input_text:
        st.error("Please enter your prompt details before describing the product.")
    elif input_text and not uploaded_image:
        st.error("Please upload your product image before describing the product.")
    else:
        st.error("Please upload your product image and prompt details before describing the product.")
