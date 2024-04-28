import shutil
from gradio_client import Client
import os

# Initialize the Gradio client
client = Client("stabilityai/TripoSR")

# Call the predict function with the image file path string
result = client.predict(
    "server\FuriAR\JJ_magdum.jpg.png", # filepath  in 'Input Image' Image component
    True, # bool  in 'Remove Background' Checkbox component
    0.85, 
    api_name="/preprocess"
)
destination_directory = "FuriAR"

# Move the processed image to the destination directory
shutil.move(result, destination_directory)

# Print the path of the moved image
print("Processed image moved to:", os.path.join(destination_directory, "image.png"))

# Call the generate function to create 3D models
result = client.predict(
    "server\FuriAR\JJ_magdum.jpg",# filepath  in 'Processed Image' Image component
    256,	# Marching Cubes Resolution
    api_name="/generate"
)
print(result)

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
            print(f"Result {i+1} moved to: {destination_path}")
        except Exception as e:
            print(f"Error moving file: {e}")
    else:
        print(f"File not found: {result_path}")
