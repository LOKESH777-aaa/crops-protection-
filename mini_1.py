# -*- coding: utf-8 -*-
"""mini-1

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/152wWyjUqhuWoUyIwNPCNyCkSfX8hNfmc
"""

pip install twilio

import os
import cv2
import numpy as np
import datetime
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.applications.imagenet_utils import decode_predictions
from google.colab import drive
from google.colab.patches import cv2_imshow
import librosa
import IPython.display as ipd
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# Mount Google Drive
drive.mount('/content/drive')

# Load the MobileNetV2 model pre-trained on ImageNet
model = MobileNetV2(weights='imagenet')

# Twilio credentials (replace with your own)
account_sid = 'AC928d4b28e380685da4d6e734cf0e3714'
auth_token = '5115b512365b45ec6807c276e1d6466e'
twilio_client = Client(account_sid, auth_token)
twilio_phone_number = '+12515515563'
owner_phone_number = '+919361150534'

# Function to preprocess the image
def preprocess_image(image_path, target_size=(224, 224)):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image at path '{image_path}' could not be loaded. Please check the file path.")
    img = cv2.resize(img, target_size)
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    img = preprocess_input(img)  # Preprocess the input according to MobileNetV2's requirements
    return img

# Function to predict the class of an image
def predict_image_class(image_path):
    preprocessed_img = preprocess_image(image_path)
    predictions = model.predict(preprocessed_img)
    decoded_predictions = decode_predictions(predictions)  # Decode the predictions
    return decoded_predictions[0]  # Return top prediction

# Function to play predator sound based on the predicted animal
def play_predator_sound(sound_file, duration):
    if os.path.exists(sound_file):
        audio_data, sr = librosa.load(sound_file, sr=None)
        ipd.display(ipd.Audio(audio_data, rate=sr, autoplay=True))
    else:
        print(f"Predator sound file '{sound_file}' not found.")

# Function to send SMS notification
def send_sms_notification(animal_label, image_path, time_of_detection):
    message_body = f"Alert: {animal_label} detected at {time_of_detection}. Image: {image_path}. Requested to inform the forest department."
    message = twilio_client.messages.create(
        body=message_body,
        from_=twilio_phone_number,
        to=owner_phone_number
    )
    print(f"Notification sent: {message.sid}")

# Function to make a voice call and play an alert sound
def make_voice_call(animal_label):
    alert_message = f"The predicted animal is a {animal_label}. Requested to inform the forest department."

    response = VoiceResponse()
    response.say(alert_message)

    call = twilio_client.calls.create(
        twiml=response,
        to=owner_phone_number,
        from_=twilio_phone_number
    )
    print(f"Call initiated: {call.sid}")

# Main function
def main():
    # Provide path to the image for classification
    image_path = "/content/drive/MyDrive/mini-1 dataset/lion/download (1).jpeg"  # Replace with the path to your image
    if not os.path.exists(image_path):
        print("Image not found!")
        return

    # Display the imported image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read the image at {image_path}.")
        return
    cv2_imshow(img)  # Use cv2_imshow to display the image

    # Predict the class of the image
    predictions = predict_image_class(image_path)

    # Get the top predicted animal and its accuracy
    top_prediction = predictions[0]
    predicted_animal = top_prediction[1]
    accuracy = top_prediction[2]

    # Print the top predicted class and its probability
    print("Top prediction:", predicted_animal)
    print("Accuracy:", accuracy)

    # Get the current time
    time_of_detection = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Send SMS notification with animal name, image, and time of detection
    send_sms_notification(predicted_animal, image_path, time_of_detection)

    # If the predicted animal has the highest accuracy, play the corresponding predator sound
    if accuracy > 0.2:  # Adjust threshold as needed
        predator_sounds = {
            "wild_boar": "/content/drive/MyDrive/tiger-attack-195840.mp3",
            "hog": "/content/drive/MyDrive/tiger-attack-195840.mp3",
            "monkey": "/content/drive/MyDrive/dog_bark.wav.mp3",
            "patas": "/content/drive/MyDrive/dog_bark.wav.mp3",
            "Indian_elephant": "/content/drive/MyDrive/christmas-fireworks-impact-174521.mp3",
            "goat": "/content/drive/MyDrive/tiger-attack-195840.mp3",
            "macaw": "/content/drive/MyDrive/sniper-fire-105896.mp3",
            "tusker":"/content/drive/MyDrive/christmas-fireworks-impact-174521.mp3"

        }
        if predicted_animal in predator_sounds:
            sound_file = predator_sounds[predicted_animal]
            play_predator_sound(sound_file, duration=5)  # Adjust duration as needed

        # Special alert for dangerous animals
        if predicted_animal in ["tiger", "lion"]:
            make_voice_call(predicted_animal)

if __name__ == "__main__":
    main()