from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import base64
import os
import csv

# Initialize Chrome WebDriver
chrome_service = Service('./chromedriver')  # Specify the path to chromedriver
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Run Chrome in headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=chrome_service, options=options)

# Set up the local directory to save images
save_directory = 'downloaded_images'
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Set up CSV file to save errorcodediv data
csv_file_path = 'errorcodes.csv'
header = ['Image Base64', 'Answer']

# Target URL (replace with the actual URL)
target_url = 'https://gen.caca01.com/ttcode/codeking'
driver.get(target_url)

# Infinite loop to continuously check for the img tag with id 'yw0'
try:
    # Read existing files in the save directory
    existing_files = os.listdir(save_directory)
    existing_image_files = [f for f in existing_files if f.startswith('downloaded_image_') and f.endswith('.png')]
    # Extract numbers from filenames and find the highest number
    count = 1
    if existing_image_files:
        counts = [int(f.split('_')[2].split('.')[0]) for f in existing_image_files if f.split('_')[2].split('.')[0].isdigit()]
        if counts:
            count = max(counts) + 1

    answered_count = 0  # Track the number of answered questions

    while True:
        try:
            # Locate the image element by id
            img_element = driver.find_element(By.ID, 'yw0')
            # Extract base64 image data from src attribute
            img_src = img_element.get_attribute('src')
            if img_src.startswith('data:image/png;base64,'):
                # Decode and save the image
                img_data = base64.b64decode(img_src.split(',')[1])
                img_path = os.path.join(save_directory, f'downloaded_image_{count}.png')    
                existing_files = os.listdir(save_directory)
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                print(f"Image downloaded and saved as {img_path}")

                count +=1 

                # Locate the input element by id and enter text
                input_element = driver.find_element(By.ID, 'code')
                input_element.send_keys('1234')  # Replace '1234' with the actual code to enter
                input_element.send_keys(Keys.ENTER)

                answered_count += 1
                if answered_count == 35:
                    # Locate all elements with class 'errorcodediv' and save to CSV
                    errorcode_elements = driver.find_elements(By.CLASS_NAME, 'errorcodediv')
                    with open(csv_file_path, mode='w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(header)  # Write header again to ensure CSV is updated correctly
                        for error_element in errorcode_elements:
                            img_tag = error_element.find_element(By.TAG_NAME, 'img')
                            img_base64 = img_tag.get_attribute('src')
                            answer_text = error_element.find_element(By.TAG_NAME, 'div').text
                            writer.writerow([img_base64, answer_text])
                    break
                continue
            else:
                print("Image source is not base64, skipping download.")
        except Exception as e:
            print(f"Waiting for image... {e}")
        
        # # Sleep for a short time before checking again
        # time.sleep(5)

except KeyboardInterrupt:
    print("Terminated by user.")
finally:
    driver.quit()