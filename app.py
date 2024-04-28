# This script will download files and folders from Google Drive.
# It performs basic URL cleaning to work with different types of links.
# Users also have access to a function that renames the latest image to "FuriAR/img2.jpeg".
from gradio_client import Client
import wget
import gdown
import argparse
import os
import shutil

def get_latest_image(folder_path):
    try:
        # Get the list of files in the folder
        files = os.listdir(folder_path)
        
        # Filter only image files
        image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        if not image_files:
            print("No image files found in the folder.")
            return None
        
        # Get the full paths of image files
        image_paths = [os.path.join(folder_path, file) for file in image_files]
        
        # Sort image files by modification time (newest first)
        image_paths.sort(key=os.path.getmtime, reverse=True)
        
        # Get the path of the latest image
        latest_image_path = image_paths[0]
        
        # Extract the filename from the path
        latest_image = os.path.basename(latest_image_path)
        
        return latest_image
    except FileNotFoundError:
        print(f"Error: '{folder_path}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def rename_to_latest_image(folder_path):
    latest_image = get_latest_image(folder_path)
    if latest_image:
        # Rename the latest image to "FuriAR/img2.jpeg"
        new_image_path = os.path.join(folder_path, "img2.jpeg")
        if os.path.exists(new_image_path):
            os.remove(new_image_path)  # Remove the existing "img2.jpeg" file
        shutil.move(os.path.join(folder_path, latest_image), new_image_path)
        print(f"Renamed {latest_image} to img2.jpeg")
        return new_image_path
    else:
        print("Failed to rename image: No image found in the folder.")
        return None

def main():
    from gradio_client import Client
    parser = argparse.ArgumentParser()
    parser.add_argument('-gfile', '--download_google_file', help="Downloads a Google File")
    parser.add_argument('-gfolder', '--download_google_folder', help="Downloads a Google Folder")
    
    args = parser.parse_args()

    if args.download_google_file:
        url = args.download_google_file
        file_id = url.split('/')[-2]

        prefix = 'https://drive.google.com/uc?/export=download&id='
        wget.download(prefix + file_id)
        print("File downloaded")

    if args.download_google_folder:
        url = args.download_google_folder
        if url.split('/')[-1] == '?usp=sharing':
            url = url.replace('?usp=sharing', '')
        gdown.download_folder(url)
        print("Folder downloaded")
        folder_path = "FuriAR"
        new_image_path = rename_to_latest_image(folder_path)
        if new_image_path:
            print(f"Latest image: {new_image_path}")

        # Initialize Gradio client
    client = Client("stabilityai/TripoSR")
    result = client.predict(
		"FuriAR\img2.jpeg",	# filepath  in 'Input Image' Image component
		api_name="/check_input_image"
        )
    print(result)
    # Call the predict function with the image file path string
    result = client.predict(
        "FuriAR\img2.jpeg", # filepath  in 'Input Image' Image component
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
        "FuriAR\image.png",# filepath  in 'Processed Image' Image component
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

if __name__ == "__main__":
    main()
    os.remove('FuriAR\image.png')

