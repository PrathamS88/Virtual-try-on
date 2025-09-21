import streamlit as st
import requests
import time
from PIL import Image
from io import BytesIO
import base64

# Configure page
st.set_page_config(
    page_title="Virtual Try-On Tool - Meesho",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Meesho-style interface with compact images
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fa;
    }
    
    .main-header {
        background: white;
        padding: 20px 0;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .meesho-logo {
        color: #9333ea;
        font-size: 1.8rem;
        font-weight: 700;
        margin-right: 2rem;
    }
    
    .page-title {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }
    
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .upload-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 2px dashed #9333ea;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-card:hover {
        border-color: #7c3aed;
        box-shadow: 0 4px 12px rgba(147, 51, 234, 0.15);
    }
    
    .garment-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 2px solid #34d399;
        text-align: center;
    }
    
    .upload-title {
        color: #9333ea;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .garment-title {
        color: #34d399;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .upload-subtitle {
        color: #6b7280;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    
    /* Compact image styles */
    .stImage {
        max-width: 100% !important;
    }
    
    .stImage > div {
        display: flex !important;
        justify-content: center !important;
    }
    
    .stImage img {
        max-width: 280px !important;
        max-height: 350px !important;
        width: auto !important;
        height: auto !important;
        object-fit: contain !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    
    /* Special styling for result image to be slightly larger */
    .result-image img {
        max-width: 320px !important;
        max-height: 400px !important;
    }
    
    .camera-options {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 1rem 0;
    }
    
    .camera-btn {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-decoration: none;
    }
    
    .camera-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .card-title {
        color: #1f2937;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-section {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .status-processing {
        background: linear-gradient(135deg, #fef3c7 0%, #fcd34d 100%);
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .status-completed {
        background: linear-gradient(135deg, #d1fae5 0%, #34d399 100%);
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .status-failed {
        background: linear-gradient(135deg, #fee2e2 0%, #f87171 100%);
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .primary-button {
        background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 1rem 0;
    }
    
    .primary-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(147, 51, 234, 0.3);
    }
    
    .secondary-button {
        background: white;
        color: #9333ea;
        border: 2px solid #9333ea;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .secondary-button:hover {
        background: #9333ea;
        color: white;
    }
    
    .image-preview {
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        max-width: 100%;
        height: auto;
    }
    
    .info-card {
        background: #f3f4f6;
        border-left: 4px solid #9333ea;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    .next-steps {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    .steps-title {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .step-item {
        color: #4b5563;
        margin: 0.5rem 0;
        padding-left: 1rem;
        position: relative;
    }
    
    .step-item::before {
        content: "•";
        color: #9333ea;
        font-weight: bold;
        position: absolute;
        left: 0;
    }
    
    .progress-container {
        background: #f3f4f6;
        border-radius: 8px;
        height: 8px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%);
        height: 100%;
        transition: width 0.3s ease;
        border-radius: 8px;
    }
    
    /* Fix text visibility and contrast */
    .stApp, .stApp > div {
        color: #1f2937 !important;
    }
    
    .stMarkdown, .stMarkdown > div {
        color: #1f2937 !important;
    }
    
    .stText, .stCaption {
        color: #4b5563 !important;
    }
    
    .stFileUploader label {
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
    
    .stFileUploader div[data-testid="stFileUploaderDropzone"] {
        background-color: #f9fafb !important;
        border: 2px dashed #9333ea !important;
        border-radius: 8px !important;
    }
    
    .stFileUploader div[data-testid="stFileUploaderDropzone"] > div {
        color: #6b7280 !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(147, 51, 234, 0.3) !important;
    }
    
    .stButton button:disabled {
        background: #d1d5db !important;
        color: #9ca3af !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    .stTextInput label, .stCheckbox label {
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
    
    .stTextInput > div > div > input {
        background-color: white !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 6px !important;
        color: #1f2937 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #9333ea !important;
        box-shadow: 0 0 0 3px rgba(147, 51, 234, 0.1) !important;
    }
    
    .stCheckbox > label > div {
        color: #1f2937 !important;
    }
    
    .stExpander details summary {
        background-color: white !important;
        color: #1f2937 !important;
        font-weight: 500 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }
    
    .stExpander details[open] {
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }
    
    .stExpander details[open] > div {
        background-color: white !important;
        color: #1f2937 !important;
    }
    
    .stProgress > div > div {
        background-color: #f3f4f6 !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%) !important;
    }
    
    .stSuccess, .stError, .stWarning, .stInfo {
        color: #1f2937 !important;
    }
    
    .stDownloadButton button {
        background: white !important;
        color: #9333ea !important;
        border: 2px solid #9333ea !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    .stDownloadButton button:hover {
        background: #9333ea !important;
        color: white !important;
    }
    
    .stCameraInput label {
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
    
    /* Compact camera input */
    .stCameraInput > div {
        max-width: 280px !important;
        margin: 0 auto !important;
    }
    
    .stCameraInput img {
        max-width: 280px !important;
        max-height: 350px !important;
        object-fit: contain !important;
        border-radius: 8px !important;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {
        display: none;
    }
    
    .stDecoration {
        display: none;
    }
    
    .css-1dp5vir {
        background-color: transparent;
    }
    
    .css-1avcm0n {
        background-color: #f8f9fa;
    }
    
    /* Compact tabs */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem !important;
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tryon_result' not in st.session_state:
    st.session_state.tryon_result = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'person_image' not in st.session_state:
    st.session_state.person_image = None

# Fixed garment image URL
GARMENT_IMAGE_URL = "https://raw.githubusercontent.com/PrathamS88/Virtual-try-on/main/Photos/BBGJ-1108-014_2_copy.webp"

def load_garment_image():
    """Load the fixed garment image from GitHub"""
    try:
        response = requests.get(GARMENT_IMAGE_URL)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            st.error(f"Failed to load garment image: HTTP {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error loading garment image: {str(e)}")
        return None

def submit_tryon_job(api_key, person_image, garment_image, fast_mode=True):
    """Submit try-on job to API"""
    submit_url = "https://tryon-api.com/api/v1/tryon"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Convert PIL images to bytes
    person_bytes = BytesIO()
    person_image.save(person_bytes, format='PNG')
    person_bytes.seek(0)
    
    garment_bytes = BytesIO()
    garment_image.save(garment_bytes, format='PNG')
    garment_bytes.seek(0)
    
    files_payload = {
        "person_images": ("person.png", person_bytes, "image/png"),
        "garment_images": ("garment.png", garment_bytes, "image/png"),
    }
    
    if fast_mode:
        files_payload["fast_mode"] = (None, "true")
    
    response = requests.post(submit_url, headers=headers, files=files_payload)
    
    if response.status_code != 202:
        raise Exception(f"Submission failed: {response.status_code} - {response.text}")
    
    return response.json()

def check_job_status(api_key, status_url):
    """Check job status"""
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    if not status_url.startswith('http'):
        check_url = f"https://tryon-api.com{status_url}"
    else:
        check_url = status_url
    
    response = requests.get(check_url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Status check failed: {response.status_code} - {response.text}")
    
    return response.json()

def get_result_image(result_data):
    """Extract image from result data"""
    # Debug: Print available keys
    available_keys = list(result_data.keys()) if result_data else []
    st.write(f"Debug - Available keys in result: {available_keys}")
    
    # Try different possible image keys
    image_keys = ["imageUrl", "image_url", "resultUrl", "result_url", "outputUrl", "output_url"]
    b64_keys = ["imageBase64", "image_base64", "resultBase64", "result_base64", "outputBase64", "output_base64", "image", "result"]
    
    # Try URL-based image retrieval
    for key in image_keys:
        if key in result_data and result_data[key]:
            image_url = result_data[key]
            st.write(f"Debug - Found image URL: {image_url}")
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    return Image.open(BytesIO(response.content))
                else:
                    st.write(f"Debug - Failed to fetch from URL {image_url}: {response.status_code}")
            except Exception as e:
                st.write(f"Debug - Error fetching from URL {image_url}: {str(e)}")
    
    # Try Base64-based image retrieval
    for key in b64_keys:
        if key in result_data and result_data[key]:
            b64_data = result_data[key]
            st.write(f"Debug - Found base64 data for key: {key}")
            try:
                # Remove data URL prefix if present
                if b64_data.startswith('data:image'):
                    b64_data = b64_data.split(',')[1]
                
                image_data = base64.b64decode(b64_data)
                return Image.open(BytesIO(image_data))
            except Exception as e:
                st.write(f"Debug - Error decoding base64 for key {key}: {str(e)}")
    
    # If no image found, print the entire result for debugging
    st.write("Debug - Full result data:")
    st.json(result_data)
    
    return None

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div class="meesho-logo">meesho</div>
            <div class="page-title">Virtual Try-On Tool</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # API Key input (in sidebar style but integrated)
    with st.expander("⚙️ Settings", expanded=False):
        col_api1, col_api2 = st.columns([2, 1])
        with col_api1:
            api_key = st.text_input(
                "API Key", 
                value="ta_a06aab8b3656461eb3333da259f2c419",
                type="password",
                help="Enter your Try-On API key"
            )
        with col_api2:
            fast_mode = st.checkbox("Fast Mode", value=True, help="Enable for faster processing")
    
    # Upload sections
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.markdown("""
        <div class="upload-card">
            <div class="upload-title">👤 Upload Person Image</div>
            <div class="upload-subtitle">Choose how you want to add your photo</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Camera and Upload options
        tab1, tab2 = st.tabs(["📷 Camera", "📁 Upload File"])
        
        with tab1:
            st.markdown("**Take a photo with your camera:**")
            camera_image = st.camera_input(
                "Take a photo",
                label_visibility="collapsed"
            )
            if camera_image:
                st.session_state.person_image = Image.open(camera_image)
        
        with tab2:
            st.markdown("**Or upload an image file:**")
            person_file = st.file_uploader(
                "Choose person image",
                type=['png', 'jpg', 'jpeg', 'webp'],
                key="person",
                label_visibility="collapsed"
            )
            if person_file:
                st.session_state.person_image = Image.open(person_file)
        
        # Display person image if available (compact size)
        if st.session_state.person_image:
            st.image(st.session_state.person_image, caption="Person Image", use_column_width=True, output_format="PNG")
    
    with col2:
        st.markdown("""
        <div class="garment-card">
            <div class="garment-title">👗 Selected Garment</div>
            <div class="upload-subtitle">This beautiful garment will be virtually tried on</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Load and display the fixed garment image (compact size)
        garment_image = load_garment_image()
        if garment_image:
            st.image(garment_image, caption="Selected Garment - Traditional Top", use_column_width=True, output_format="PNG")
        else:
            st.error("Failed to load the garment image. Please check your internet connection.")
    
    # Try-on button
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button(
        "🚀 Generate Virtual Try-On", 
        disabled=not (st.session_state.person_image and garment_image and api_key and not st.session_state.processing),
        type="primary",
        use_container_width=True
    ):
        if st.session_state.person_image and garment_image and api_key:
            st.session_state.processing = True
            st.session_state.tryon_result = None
            
            try:
                # Show processing status
                status_placeholder = st.empty()
                progress_placeholder = st.empty()
                
                with status_placeholder.container():
                    st.markdown('<div class="status-processing">🔄 Submitting try-on job...</div>', 
                              unsafe_allow_html=True)
                
                # Progress bar
                with progress_placeholder.container():
                    progress_bar = st.progress(0)
                
                # Submit job
                job_response = submit_tryon_job(api_key, st.session_state.person_image, garment_image, fast_mode)
                job_id = job_response.get("jobId")
                status_url = job_response.get("statusUrl")
                
                progress_bar.progress(25)
                
                with status_placeholder.container():
                    st.markdown(f'<div class="status-processing">⏳ Processing job {job_id}...</div>', 
                              unsafe_allow_html=True)
                
                # Poll for result indefinitely until completion
                poll_interval = 3
                elapsed = 0
                result_json = None
                
                while True:
                    time.sleep(poll_interval)
                    elapsed += poll_interval
                    
                    # Update progress (will cycle back after reaching 95%)
                    progress = 25 + ((elapsed % 60) / 60) * 70
                    progress_bar.progress(int(progress))
                    
                    with status_placeholder.container():
                        st.markdown(f'<div class="status-processing">⏳ Processing job {job_id}... ({elapsed}s elapsed)</div>', 
                                  unsafe_allow_html=True)
                    
                    try:
                        resp_json = check_job_status(api_key, status_url)
                        status = resp_json.get("status")
                        
                        if status == "completed":
                            result_json = resp_json
                            break
                        elif status == "failed":
                            error_msg = resp_json.get("error", "Unknown error")
                            error_code = resp_json.get("errorCode", "")
                            raise Exception(f"Try-on generation failed: {error_msg} (Code: {error_code})")
                        
                        # Continue polling for "processing" or other statuses
                        
                    except Exception as e:
                        if "failed" in str(e).lower():
                            # If it's a job failure, break the loop
                            raise e
                        else:
                            # If it's a network/API error, continue polling
                            st.warning(f"Status check error (will retry): {str(e)}")
                            continue
                
                if result_json is None:
                    raise Exception("Unexpected error: No result received")
                
                progress_bar.progress(100)
                
                # Get result image
                st.write("Debug - Attempting to extract image from result...")
                result_image = get_result_image(result_json)
                
                if result_image:
                    st.session_state.tryon_result = result_image
                    with status_placeholder.container():
                        st.markdown('<div class="status-completed">✅ Try-on completed successfully!</div>', 
                                  unsafe_allow_html=True)
                    st.success("🎉 Virtual try-on completed! Check the result below.")
                    # Force refresh the page to show the result
                    time.sleep(1)  # Small delay to ensure state is saved
                    st.rerun()
                else:
                    st.error("❌ No image found in the result. Check the debug information above.")
                    st.write("Full API response:")
                    st.json(result_json)
            
            except Exception as e:
                with status_placeholder.container():
                    st.markdown(f'<div class="status-failed">❌ Error: {str(e)}</div>', 
                              unsafe_allow_html=True)
                st.error(f"Try-on failed: {str(e)}")
            
            finally:
                st.session_state.processing = False
                if 'progress_bar' in locals():
                    progress_bar.empty()
    
    # Results section
    if st.session_state.tryon_result:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="result-card">
            <div class="card-title">✨ AI Generated Try-On Result</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display result in center with compact size
        col_result = st.columns([1, 2, 1])
        with col_result[1]:
            # Apply special CSS class for result image
            st.markdown('<div class="result-image">', unsafe_allow_html=True)
            st.image(
                st.session_state.tryon_result, 
                caption="Virtual Try-On Result", 
                use_column_width=True,
                output_format="PNG"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download button
            buf = BytesIO()
            st.session_state.tryon_result.save(buf, format='PNG')
            st.download_button(
                label="📥 Download Result",
                data=buf.getvalue(),
                file_name="tryon_result.png",
                mime="image/png",
                use_container_width=True,
                type="secondary"
            )
        
        # Next steps section
        st.markdown("""
        <div class="result-card">
            <div class="card-title">📋 Next Steps</div>
            <div class="next-steps">
                <div class="steps-title">Based on the AI review, consider these actions:</div>
                <div class="step-item">Review the generated try-on result for accuracy</div>
                <div class="step-item">Download the image if satisfied with the result</div>
                <div class="step-item">Try different poses or lighting for more variations</div>
                <div class="step-item">Use the result for your product listings or marketing</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Info card when no result yet
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card">
            <strong>How it works:</strong><br>
            1. Take a photo with your camera or upload a clear photo of yourself<br>
            2. The selected traditional garment will be virtually tried on<br>
            3. Click "Generate Virtual Try-On" and wait for the AI to process<br>
            4. Download your result when ready!
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close main container

if __name__ == "__main__":
    main()
