import streamlit as st
import requests
import time
from PIL import Image
from io import BytesIO
import base64

# Configure page
st.set_page_config(
    page_title="Virtual Try-On Studio",
    page_icon="👓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #2E86AB;
        margin: 10px 0;
    }
    
    .result-section {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .try-on-btn {
        background: #2E86AB;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
    }
    
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    
    .status-processing {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-completed {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-failed {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .image-preview {
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        max-width: 100%;
        height: auto;
    }
    
    .sidebar-section {
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tryon_result' not in st.session_state:
    st.session_state.tryon_result = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

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
    st.markdown('<h1 class="main-header">👓 Virtual Try-On Studio</h1>', unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("⚙️ Settings")
        
        # API Key input
        api_key = st.text_input(
            "API Key", 
            value="ta_fce0b1a247b9437ea1b3785e1718724e",
            type="password",
            help="Enter your Try-On API key"
        )
        
        # Fast mode toggle
        fast_mode = st.checkbox("Fast Mode", value=True, help="Enable for faster processing")
        
        # Polling interval
        poll_interval = st.slider("Poll Interval (seconds)", 2, 10, 3, help="How often to check job status")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Instructions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("📋 Instructions")
        st.markdown("""
        1. **Upload Person Image**: Upload a clear photo of the person
        2. **Upload Garment Image**: Upload the clothing item to try on
        3. **Click Try-On**: Start the virtual try-on process (no time limit)
        4. **View Result**: See the generated try-on result
        
        **Note**: The process will continue until completion, regardless of how long it takes.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("👤 Upload Person Image")
        person_file = st.file_uploader(
            "Choose person image",
            type=['png', 'jpg', 'jpeg', 'webp'],
            key="person"
        )
        
        if person_file:
            person_image = Image.open(person_file)
            st.image(person_image, caption="Person Image", use_column_width=True, output_format="PNG")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("👕 Upload Garment Image")
        garment_file = st.file_uploader(
            "Choose garment image",
            type=['png', 'jpg', 'jpeg', 'webp'],
            key="garment"
        )
        
        if garment_file:
            garment_image = Image.open(garment_file)
            st.image(garment_image, caption="Garment Image", use_column_width=True, output_format="PNG")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.subheader("✨ Try-On Result")
        
        if st.session_state.tryon_result:
            st.image(
                st.session_state.tryon_result, 
                caption="Virtual Try-On Result", 
                use_column_width=True,
                output_format="PNG"
            )
            
            # Download button
            buf = BytesIO()
            st.session_state.tryon_result.save(buf, format='PNG')
            st.download_button(
                label="📥 Download Result",
                data=buf.getvalue(),
                file_name="tryon_result.png",
                mime="image/png",
                use_container_width=True
            )
        else:
            st.info("Upload images and click 'Start Try-On' to see the result here!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Try-on button and processing
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        if st.button(
            "🚀 Start Virtual Try-On", 
            disabled=not (person_file and garment_file and api_key and not st.session_state.processing),
            use_container_width=True,
            type="primary"
        ):
            if person_file and garment_file and api_key:
                st.session_state.processing = True
                st.session_state.tryon_result = None
                
                try:
                    # Show processing status
                    status_placeholder = st.empty()
                    progress_bar = st.progress(0)
                    
                    with status_placeholder.container():
                        st.markdown('<div class="status-box status-processing">🔄 Submitting try-on job...</div>', 
                                  unsafe_allow_html=True)
                    
                    # Submit job
                    person_image = Image.open(person_file)
                    garment_image = Image.open(garment_file)
                    
                    job_response = submit_tryon_job(api_key, person_image, garment_image, fast_mode)
                    job_id = job_response.get("jobId")
                    status_url = job_response.get("statusUrl")
                    
                    progress_bar.progress(25)
                    
                    with status_placeholder.container():
                        st.markdown(f'<div class="status-box status-processing">⏳ Processing job {job_id}...</div>', 
                                  unsafe_allow_html=True)
                    
                    # Poll for result indefinitely until completion
                    poll_interval = st.session_state.get('poll_interval', 3)
                    elapsed = 0
                    result_json = None
                    
                    while True:
                        time.sleep(poll_interval)
                        elapsed += poll_interval
                        
                        # Update progress (will cycle back after reaching 95%)
                        progress = 25 + ((elapsed % 60) / 60) * 70
                        progress_bar.progress(int(progress))
                        
                        with status_placeholder.container():
                            st.markdown(f'<div class="status-box status-processing">⏳ Processing job {job_id}... ({elapsed}s elapsed)</div>', 
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
                            st.markdown('<div class="status-box status-completed">✅ Try-on completed successfully!</div>', 
                                      unsafe_allow_html=True)
                        st.success("🎉 Virtual try-on completed! Check the result in the right panel.")
                        # Force refresh the page to show the result
                        time.sleep(1)  # Small delay to ensure state is saved
                        st.rerun()
                    else:
                        st.error("❌ No image found in the result. Check the debug information above.")
                        st.write("Full API response:")
                        st.json(result_json)
                
                except Exception as e:
                    with status_placeholder.container():
                        st.markdown(f'<div class="status-box status-failed">❌ Error: {str(e)}</div>', 
                                  unsafe_allow_html=True)
                    st.error(f"Try-on failed: {str(e)}")
                
                finally:
                    st.session_state.processing = False
                    if 'progress_bar' in locals():
                        progress_bar.empty()

if __name__ == "__main__":
    main()