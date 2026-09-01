'''hybrid
july 2nd
'''


import os
import time
import base64
import requests
from PIL import Image, ImageOps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------- Image Preprocessing ----------

def add_padding(image_path, padding=100):
    img = Image.open(image_path)
    padded = ImageOps.expand(img, border=padding, fill='white')
    padded_path = image_path.replace(".png", "_padded.png").replace(".jpg", "_padded.jpg")
    padded.save(padded_path)
    return padded_path

# ---------- Image Saving Logic ----------

def save_base64_image(data_url, output_path):
    try:
        header, encoded = data_url.split(",", 1)
        data = base64.b64decode(encoded)
        with open(output_path, "wb") as f:
            f.write(data)
        print(f"Saved base64: {output_path}")
        return True
    except Exception as e:
        print(f"Failed to save base64 image: {e}")
        return False

def download_image_by_url(url, output_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Saved URL image: {output_path}")
            return True
    except Exception as e:
        print(f"Failed to download image from URL: {e}")
    return False

def save_image_from_src(src, output_path):
    if src.startswith("data:image/"):
        return save_base64_image(src, output_path)
    elif src.startswith("http"):
        return download_image_by_url(src, output_path)
    else:
        print(f"Unsupported image format: {src[:30]}")
        return False

# ---------- Google Lens Handler ----------

def download_images_google_lens(driver, image_path, output_dir, max_images=50, min_size=32):
    print(f"\nProcessing: {os.path.basename(image_path)}")
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    padded_path = add_padding(image_path, padding=100)

    driver.get("https://images.google.com/?hl=en")
    time.sleep(2)

    try:
        # Click Lens button
        try:
            lens_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][@aria-label='Search by image']"))
            )
        except:
            lens_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][@aria-label='이미지로 검색']"))
            )
        lens_button.click()
        time.sleep(2)

        # Upload the image
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        file_input.send_keys(os.path.abspath(padded_path))
        time.sleep(10)

        # Scroll to load more images
        for _ in range(10):
            driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(1)

        # Locate image elements
        img_elements = driver.find_elements(By.XPATH, "//img[starts-with(@src, 'data:image/') or contains(@src, 'gstatic.com')]")
        print(f"Found {len(img_elements)} image(s)")

        os.makedirs(output_dir, exist_ok=True)
        count = 0

        for idx, img in enumerate(img_elements):
            if count >= max_images:
                break

            src = img.get_attribute("src")

            if not src:
                continue

            # Skip known junk patterns
            if (
                "favicon" in src or
                "logo" in src or
                "favicon-tbn" in src
            ):
                print(f"Skipped by pattern: {src[:80]}")
                continue

            # Skip small images
            try:
                width = driver.execute_script("return arguments[0].naturalWidth;", img)
                height = driver.execute_script("return arguments[0].naturalHeight;", img)
                if width <= min_size and height <= min_size:
                    print(f"Skipped small image ({width}x{height})")
                    continue
            except Exception as e:
                print(f"Error getting image size: {e}")
                continue

            # Save valid image
            filename = os.path.join(output_dir, f"{base_name}_similar_{count + 1}.png")
            if save_image_from_src(src, filename):
                count += 1

        if count == 0:
            print("No valid images saved.")

    except Exception as e:
        print(f"Error during processing: {e}")

# ---------- Batch Mode ----------

def batch_download_google_lens(input_folder, output_folder, max_images_per_input=10):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        os.makedirs(output_folder, exist_ok=True)
        image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        for image_file in image_files:
            full_path = os.path.join(input_folder, image_file)
            download_images_google_lens(driver, full_path, output_folder, max_images_per_input)

    finally:
        driver.quit()
        print("\n Done. All images processed.")

# ---------- Run ----------
if __name__ == "__main__":
    batch_download_google_lens(
        input_folder="/Users/shwetakc/pythonProject3/reverse_image_search/seed/testjimmy",
        output_folder="/Users/shwetakc/pythonProject3/reverse_image_search/seed/testjimmy/output",
        max_images_per_input=50
    )
