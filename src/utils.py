import os
import hashlib
import requests
import logging
from logging.handlers import RotatingFileHandler

# Set to store processed URLs to avoid duplicates
processed_urls = set()

def setup_logger():
    """
    Sets up a logger with a rotating file handler.
    Logs are saved to 'logs/scraper.log' and rotate when they reach 5MB.
    """
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler = RotatingFileHandler('logs/scraper.log', maxBytes=5 * 1024 * 1024, backupCount=2)
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    return logger

def save_image(img_url, logger):
    """
    Downloads and saves an image from a given URL.
    Avoids downloading duplicates by checking processed URLs and file content.
    """
    if img_url in processed_urls:
        logger.info(f"Duplicate URL skipped: {img_url}")
        return

    try:
        response = requests.get(img_url, stream=True)
        response.raise_for_status()

        img_name = os.path.basename(img_url)
        img_path = os.path.join('images', img_name)

        # Check if the image file already exists and if it's a duplicate
        if os.path.exists(img_path) and is_duplicate_image(img_path, response.content):
            logger.info(f"Duplicate image file skipped: {img_name}")
            return

        # Save the image
        with open(img_path, 'wb') as img_file:
            for chunk in response.iter_content(1024):
                img_file.write(chunk)
        logger.info(f"Saved image: {img_name}")

        # Mark the URL as processed
        processed_urls.add(img_url)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image {img_url}: {e}")

def is_duplicate_image(file_path, new_image_content):
    """
    Compares the MD5 hash of an existing file with that of new content to detect duplicates.
    """
    existing_hash = calculate_md5(file_path)
    new_hash = hashlib.md5(new_image_content).hexdigest()
    return existing_hash == new_hash

def calculate_md5(file_path):
    """
    Calculates the MD5 hash of a file for comparison.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_images_folder():
    """
    Creates the images folder if it doesn't exist.
    """
    if not os.path.exists('images'):
        os.makedirs('images')