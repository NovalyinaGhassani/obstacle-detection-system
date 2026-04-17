import os
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Fungsi untuk membuat folder jika belum ada
def create_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Fungsi untuk download gambar dari URL
def download_image(url, folder, img_name):
    try:
        urllib.request.urlretrieve(url, os.path.join(folder, img_name))
        print(f"Downloaded {img_name}")
    except Exception as e:
        print(f"Failed to download {img_name}: {e}")

def scrape_images(keyword, folder_path, num_images=10):
    # Menggunakan WebDriver Manager untuk otomatisasi
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    search_url = f"https://www.google.com/search?q={keyword}&tbm=isch"
    driver.get(search_url)

    # Scroll untuk memuat lebih banyak gambar
    body = driver.find_element(By.TAG_NAME, 'body')
    
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # Ambil elemen gambar (thumbnail)
    images = driver.find_elements(By.CSS_SELECTOR, 'img.YQ4gaf')  # Ganti selector jika perlu

    img_count = 0
    for img in images:
        try:
            img.click()  # Klik untuk memperbesar gambar
            time.sleep(2)  # Tunggu untuk gambar diperbesar
            
            # Ambil elemen gambar yang diperbesar
            large_image = driver.find_element(By.CSS_SELECTOR, 'img.sFlh5c.FyHeAf.iPVvYb')  # Selector untuk gambar yang diperbesar
            img_url = large_image.get_attribute('src')
            print(f"Found image URL: {img_url}")  # Logging URL yang ditemukan

            # Download gambar jika URL valid
            if img_url and 'http' in img_url:
                img_name = f"{keyword.replace(' ', '_')}_{img_count}.jpg"
                print(f"Downloading image: {img_name}")
                download_image(img_url, folder_path, img_name)
                img_count += 1

            if img_count >= num_images:
                break
            
        except Exception as e:
            print(f"Error: {e}")

    driver.quit()

# Main function
if __name__ == "__main__": 
    BASE_DIR = os.path.join(os.getcwd(), "dataset")
    create_folder(BASE_DIR)

    keywords = ["dredging vessel", "kapal isap pasir laut", "kapal keruk pasir"]
    num_images = 100  # Jumlah gambar per keyword

    for keyword in keywords:
        folder_name = keyword.replace(' ', '_')
        folder_path = os.path.join(BASE_DIR, folder_name)
        
        create_folder(folder_path)
        print(f"Scraping images for: {keyword}")
        
        scrape_images(keyword, folder_path, num_images)
