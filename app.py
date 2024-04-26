from flask import Flask, render_template
import speech_recognition as sr
from happytransformer import HappyTextToText, TTSettings
import os

app = Flask(__name__)

def listen_and_save_text():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use default microphone as audio source
    with sr.Microphone() as source:
        print("Listening...")

        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source)

        # Listen for user input
        audio = recognizer.listen(source)

        try:
            print("Recognizing speech...")
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            print("You said:", text)

            # Save recognized text to a file
            filename = "speech_output.txt"
            with open(filename, "w") as file:
                file.write(text)
            print("Speech saved to", filename)

            return filename, text

        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")
            return None, None
        except sr.RequestError as e:
            print("Error:", e)
            return None, None

def grammar_checker(file_path):
    # Function to read text from a .txt file
    def read_text_from_file(file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        return text

    # Function to save text to a .txt file
    def save_text_to_file(text, filename):
        with open(filename, "w") as file:
            file.write(text)
        print("Corrected text saved to", filename)

    # Initialize HappyTextToText with T5 model and grammar correction model
    happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")

    # Set TTSettings for generation
    args = TTSettings(num_beams=5, min_length=1)

    # Read text from the file
    input_text = read_text_from_file(file_path)

    # Generate corrected text using the grammar correction model
    corrected_text = happy_tt.generate_text("grammar: " + input_text, args=args).text

    # Save corrected text to a .txt file
    corrected_file_path = "corrected_text.txt"
    save_text_to_file(corrected_text, corrected_file_path)

    # Print the corrected text and error count
    print("Corrected Text:")
    print(corrected_text)
    return corrected_text

def count_changes(original_file_path, corrected_file_path):
    # Read text from the original file
    with open(original_file_path, 'r') as file:
        original_text = file.read().split()

    # Read text from the corrected file
    with open(corrected_file_path, 'r') as file:
        corrected_text = file.read().split()
    total_words = len(corrected_text)
    print(f"total number of words :{total_words}")
    # Define special characters to ignore
    special_characters = ['?', '.', '!', ',', ';']

    # Count the number of changes
    change_count = 0
    change_details = []  # Store details of each change
    
    for original_word, corrected_word in zip(original_text, corrected_text):
        # Ignore special characters
        if original_word in special_characters or corrected_word in special_characters:
            continue
        
        # Convert words to lowercase for comparison
        original_word_lower = original_word.lower()
        corrected_word_lower = corrected_word.lower()

        # Ignore changes caused by converting lowercase to uppercase
        if original_word_lower == corrected_word_lower:
            continue

        # Increment change_count for other changes
        change_count += 1

        # Add the identified change details to the list
        change_details.append(f"Change identified: Original '{original_word}' -> Corrected '{corrected_word}'")

    # Save the count of changes to error.txt
    with open("error.txt", "w") as error_file:
        error_file.write(f"{change_count}")
    return change_count

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hr_interview')
def hr_interview():
    file_path, _ = listen_and_save_text()
    if file_path:
        corrected_text = grammar_checker(file_path)
        count_changes(file_path, "corrected_text.txt")
    return render_template('hr_interview.html')

@app.route('/technical_interview')
def technical_interview():
    return render_template('technical_interview.html')

if __name__ == '__main__':
    app.run(debug=True)
