import os
import shutil
import streamlit as st
from gradio_client import Client

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
st.title("Upload Image and Process")

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

    result = client.predict(
        "FuriAR/image.png",  # filepath  in 'Processed Image' Image component
        256,                 # Marching Cubes Resolution
        api_name="/generate"
    )
    st.write("Generate Result:", result)

    # Create a subfolder within the "Model" directory to store the files
    model_folder = os.path.join("Model", "3D_Models")
    os.makedirs(model_folder, exist_ok=True)

    # Move each result to the subfolder within the "Model" directory
    for i, result_path in enumerate(result):
        if os.path.exists(result_path):
            try:
                filename = os.path.basename(result_path)
                destination_path = os.path.join(model_folder, filename)
                shutil.move(result_path, destination_path)
                st.write(f"Result {i+1} moved to: {destination_path}")
            except Exception as e:
                st.error(f"Error moving file: {e}")
        else:
            st.error(f"File not found: {result_path}")