from openai import OpenAI
import time
import requests
import base64
import os
import cv2
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import faulthandler

faulthandler.enable()

# Define the directory containing the images
image_dir = '/Users/julian/dddd_trainer/downloaded_images_training_data_copy_2'

# Initialize the lists for true and predicted labels
y_true = []
y_pred = []

# Initialize OpenAI client
client = OpenAI(
    base_url=os.environ["TRENDMICRO_API_BASE_URL"],
    api_key=os.environ["TRENDMICRO_API_KEY"],
)

def encode_image(image_path):
    """Convert an image to a base64-encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Iterate through only 200 PNG files in the directory
for index, filename in enumerate(os.listdir(image_dir)):
    if index >= 200:
        break  # Stop after processing 200 images
    
    if filename.endswith('.png'):

        # Extract the true label from the filename
        label = filename.split('_')[0]

        # Get the full path of the image
        image_path = os.path.join(image_dir, filename)
        
        # Convert the image to base64
        base64_image = encode_image(image_path)

        # Send the image to OpenAI for text extraction
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Just give me the four English letters of the image without space, no need for other words or punctuation"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )

        # Extract the predicted text
        predicted_text = response.choices[0].message.content.strip()

        # Add the true and predicted labels to the lists
        y_true.append(label)
        y_pred.append(predicted_text)

        # Determine if the prediction was successful
        status = '成功' if predicted_text == label else '失敗'

        # Print the filename, true label, predicted result, and status
        print(f"文件名: {filename}, 真實標籤: {label}, 預測結果: {predicted_text}, 預測{status}")

# Calculate and print metrics
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, average='weighted', zero_division=1)
recall = recall_score(y_true, y_pred, average='weighted', zero_division=1)
f1 = f1_score(y_true, y_pred, average='weighted', zero_division=1)

print(f"\n準確率 (Accuracy): {accuracy:.4f}")
print(f"精確率 (Precision): {precision:.4f}")
print(f"召回率 (Recall): {recall:.4f}")
print(f"F1-score: {f1:.4f}")

print("\n分類報告 (Classification Report):")
print(classification_report(y_true, y_pred, zero_division=1))
