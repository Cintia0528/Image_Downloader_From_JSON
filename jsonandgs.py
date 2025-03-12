import streamlit as st
import json
import requests
import zipfile
from io import BytesIO

# Title
st.title("📥 JSON & URL Image Downloader")

# Upload JSON file or paste JSON text
uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
json_text = st.text_area("Or paste JSON here")

# Input for URLs
url_input = st.text_area("Or paste image URLs (one per line)")

# Load JSON
data = None
if uploaded_file:
    data = json.load(uploaded_file)
elif json_text:
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        st.error("Invalid JSON format!")

# Process JSON if valid
if data:
    st.success("JSON loaded successfully!")

    # Extract unique image URLs
    downloaded_urls = set()
    image_urls = []

    for app in data.get("apps", []):
        for key in ["imageUri", "backgroundImageUri"]:
            if key in app and app[key] not in downloaded_urls:
                downloaded_urls.add(app[key])
                image_urls.append(app[key])

# Process URLs from user input
if url_input:
    urls = url_input.splitlines()
    for url in urls:
        if url not in downloaded_urls:
            downloaded_urls.add(url)
            image_urls.append(url)

# Download images as ZIP
if image_urls:
    st.write(f"Found {len(image_urls)} unique images.")
    
    zip_buffer = BytesIO()
    with requests.Session() as session:
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for url in image_urls:
                try:
                    response = session.get(url, stream=True)
                    if response.status_code == 200:
                        filename = url.split("/")[-1]
                        zip_file.writestr(filename, response.content)
                except Exception as e:
                    st.warning(f"Failed to download {url}: {e}")

    # Provide ZIP file download
    zip_buffer.seek(0)
    st.download_button("Download All Images", zip_buffer, "images.zip", "application/zip")
else:
    st.warning("No images found!")
