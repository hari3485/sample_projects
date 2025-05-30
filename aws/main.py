import streamlit as st
import os
import tempfile
import uuid
from PIL import Image
from dotenv import load_dotenv
import traceback
from src.tools.aws_cost_generator.tool import AWS_Cost_Generator_Tool
from src.tools.aws_diagram_generator.tool import AWS_Diagram_Generator_Tool

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="AWS Architecture Tools",
    page_icon="☁️",
    layout="wide"
)

def generate_random_filename():
    """Generates a random filename for the diagram."""
    return f"aws_diagram_{uuid.uuid4().hex[:8]}"

# Initialize session state
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'aws_diagram_path' not in st.session_state:
    st.session_state.aws_diagram_path = None
if 'cost_analysis' not in st.session_state:
    st.session_state.cost_analysis = None

# Main UI
st.title(" AWS Architecture Tools")
st.session_state.image_prompt="Convert the given architecture diagram image into an AWS architecture diagram by aligning all components like APIs, databases, servers, and storage with suitable AWS services, while maintaining the original data flow.",
st.session_state.cost_prompt="What AWS services are used in this architecture? Provide detailed cost analysis.",


# Step 1: Image Upload
st.header("Step 1: Upload Architecture Diagram")
uploaded_file = st.file_uploader(
    "Choose an image file", 
    type=['png', 'jpg', 'jpeg'],
    help="Upload an architecture diagram that you want to convert to AWS architecture"
)

if uploaded_file is not None:
    # Display uploaded image
    st.session_state.uploaded_image = uploaded_file
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader(" Uploaded Image")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

# Step 2: AWS Diagram Generation
st.header("Step 2: Generate AWS Architecture Diagram")

if st.session_state.uploaded_image is not None:
    if st.button(" Generate AWS Diagram", type="primary"):
        with st.spinner("Generating AWS architecture diagram..."):
            try:
                # Read image bytes
                st.session_state.uploaded_image.seek(0)
                image_bytes = st.session_state.uploaded_image.read()
                import tempfile

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(image_bytes)
                    tmp_path = tmp.name

                # Initialize diagram generator
                diagram_tool = AWS_Diagram_Generator_Tool(model_string="openai/gpt-4.1")
                
                # Generate diagram
                metadata,result = diagram_tool.execute(tmp_path, st.session_state.image_prompt)
                st.json(metadata)

                if "error" in result:
                    st.error(f"Error generating diagram: {result['error']}")
                elif "image" in result:
                    st.session_state.aws_diagram_path = result["image"]
                    st.success(" AWS diagram generated successfully!")
                    
                else:
                    st.error("Unexpected result format")


            except Exception as e:
                traceback.print_exc(e)
                st.error(f"Error: {str(e)}")
else:
    st.info(" Please upload an image first to generate AWS diagram")

# Step 3: Cost Analysis


if st.session_state.aws_diagram_path is not None:
    # --- START OF CODE TO DISPLAY THE AWS DIAGRAM ---
    # Display the AWS diagram as a reference for cost analysis
    if os.path.exists(st.session_state.aws_diagram_path):
        st.image(
            st.session_state.aws_diagram_path,
            use_container_width=True
        )

    else:
        # This warning appears if the path is stored in session_state but the file is missing.
        st.warning(
            "The AWS diagram image file seems to be missing. "
            "Cost analysis might not be accurate or possible. "
            "Please ensure the diagram was generated correctly in Step 2, or try regenerating it."
        )
    # --- END OF CODE TO DISPLAY THE AWS DIAGRAM ---
    
    st.header(" Step 3: AWS Cost Analysis")
    if st.button(" Generate Cost Analysis", type="primary"):
        with st.spinner("Calculating AWS costs..."):
            try:
                # Read the generated AWS diagram
                with open(st.session_state.aws_diagram_path, 'rb') as f:
                    aws_diagram_bytes = f.read()
                
                # Initialize cost generator
                cost_tool = AWS_Cost_Generator_Tool(model_string="openai/gpt-4.1")
                
                # Generate cost analysis
                metadata,cost_result = cost_tool.execute(st.session_state.aws_diagram_path, st.session_state.cost_prompt)
                st.json(metadata)
                
                if "error" in str(cost_result):
                    st.error(f"Error generating cost analysis: {cost_result}")
                else:
                    st.session_state.cost_analysis = cost_result
                    st.success(" Cost analysis generated successfully!")
                    
                    # Display cost analysis
                    st.markdown(cost_result)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.info(" Please generate an AWS diagram first to perform cost analysis")

