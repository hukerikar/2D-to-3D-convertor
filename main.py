import os
import shutil
import streamlit as st
from gradio_client import Client
import base64
import os
import shutil
import streamlit as st

def clear_model_folders():
    glb_folder = "Model/GLB"
    obj_folder = "Model/OBJ"
    
    # Remove all files inside the GLB folder
    for file_name in os.listdir(glb_folder):
        file_path = os.path.join(glb_folder, file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            st.error(f"Failed to delete {file_path}: {e}")
    
    # Remove all files inside the OBJ folder
    for file_name in os.listdir(obj_folder):
        file_path = os.path.join(obj_folder, file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            st.error(f"Failed to delete {file_path}: {e}")

# Create a button to clear the model folders
if st.button("Clear"):
    clear_model_folders()
    st.success("Model folders cleared successfully!")

def get_binary_file_downloader_html(data, file_name, button_label):
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{file_name}">{button_label}</a>'
    return href

# Function to rename and save the uploaded image
def rename_and_save_image(uploaded_file):
    try:
        # Create the save directory if it doesn't exist
        os.makedirs("FuriAR", exist_ok=True)
        
        # Define the path for saving the renamed image
        save_path = os.path.join("FuriAR", "image.png")
        
        # Rename the uploaded file to "image.png" and move it to the save directory
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return save_path
    except Exception as e:
        return f"Error renaming and saving image: {e}"

# Streamlit UI
st.title("FURI-AR")

# Upload or drag and drop an image file
uploaded_file = st.file_uploader("Upload an Image File", type=["jpg", "jpeg", "png"])

# Process the uploaded image if available 
if uploaded_file is not None:
    # Rename and save the uploaded image
    renamed_image_path = rename_and_save_image(uploaded_file)
    st.success(f"Image uploaded and renamed to: {renamed_image_path}")

    # Initialize Gradio client
    client = Client("stabilityai/TripoSR")
    
    # Call the predict function with the image file path string
    result = client.predict(
        "FuriAR/image.png",  # filepath  in 'Input Image' Image component
        api_name="/check_input_image"
    )
    st.write("Check Input Image Result:", result)

    result = client.predict(
        "FuriAR/image.png",  # filepath  in 'Input Image' Image component
        True,                # bool  in 'Remove Background' Checkbox component
        0.85,                # float (numeric value between 0.5 and 1.0) in 'Foreground Ratio' Slider component
        api_name="/preprocess"
    )
    st.write("Preprocess Result:", result)

    # Store the processed image in FuriAR folder with the same name as uploaded image
    processed_image_path = os.path.join("FuriAR", "image.png")
    shutil.move(result, processed_image_path)  # Extract the file path from the tuple
    st.write("Processed Image replaced at:", processed_image_path)

    result = client.predict(
        "FuriAR/image.png",  # filepath  in 'Processed Image' Image component
        256,                 # Marching Cubes Resolution
        api_name="/generate"
    )
    st.write("Generate Result:", result)

    # Create subfolders within the "Model" directory to store the files
    glb_folder = os.path.join("Model", "GLB")
    obj_folder = os.path.join("Model", "OBJ")
    os.makedirs(glb_folder, exist_ok=True)
    os.makedirs(obj_folder, exist_ok=True)

    # Move each result to the corresponding subfolder within the "Model" directory
    for i, result_path in enumerate(result):
        if os.path.exists(result_path):
            try:
                filename = os.path.basename(result_path)
                if filename.lower().endswith('.glb'):
                    destination_path = os.path.join(glb_folder, filename)
                elif filename.lower().endswith('.obj'):
                    destination_path = os.path.join(obj_folder, filename)
                else:
                    st.error(f"Unsupported file format: {filename}")
                    continue
                shutil.move(result_path, destination_path)
                st.write(f"Result {i+1} moved to: {destination_path}")
            except Exception as e:
                st.error(f"Error moving file: {e}")
        else:
            st.error(f"File not found: {result_path}")
    
    # Automatically download the processed image and .glb model
    if os.path.exists(processed_image_path):
        processed_image_data = open(processed_image_path, 'rb').read()
        st.markdown(get_binary_file_downloader_html(processed_image_data, 'image.png', 'Download Processed Image'), unsafe_allow_html=True)
    else:
        st.warning("Processed image not found for download.")

    glb_files = [f for f in os.listdir(glb_folder) if f.endswith('.glb')]
    if glb_files:
        for glb_file in glb_files:
            glb_file_path = os.path.join(glb_folder, glb_file)
            glb_file_data = open(glb_file_path, 'rb').read()
            st.markdown(get_binary_file_downloader_html(glb_file_data, glb_file, f'Download {glb_file}'), unsafe_allow_html=True)
    else:
        st.warning("No .glb files found for download.")
    st.write("Thanks for visiting (~ from Srujan Hukerikar)")