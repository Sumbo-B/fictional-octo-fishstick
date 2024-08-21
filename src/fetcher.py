import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import random
import time
from src.config import USER_AGENTS, PROXIES

def is_page_static(url):
    """
    Determines if a page is likely static by checking if it contains
    any `<script>` tags. If there are many scripts, it’s likely dynamic.
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # If the page has more than a few <script> tags, it's likely dynamic
        return len(soup.find_all('script')) < 5
    except requests.exceptions.RequestException as e:
        print(f"Error checking if page is static: {e}")
        return False  # Assume dynamic if we can’t determine

def fetch_page(url, retries=3):
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }
    proxy = {"http": random.choice(PROXIES), "https": random.choice(PROXIES)} if PROXIES else None

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, proxies=proxy)
            response.raise_for_status()

            # Explicitly decode the content as UTF-8
            content = response.content.decode('utf-8', errors='replace')

            time.sleep(random.uniform(0.5, 1.5))  # Random delay to avoid detection
            return content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {url} on attempt {attempt + 1} - {e}")
            time.sleep(2)
            if attempt + 1 == retries:
                print(f"Failed to fetch URL after {retries} attempts: {url}")
                return None

def fetch_dynamic_page(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    time.sleep(3)  # Adjust sleep time based on page complexity
    rendered_html = driver.page_source
    driver.quit()
    
    return rendered_html

def fetch_infinite_scroll_page(url, scroll_pause_time=2, max_scrolls=10):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0

    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

        last_height = new_height
        scrolls += 1

    rendered_html = driver.page_source
    driver.quit()
    
    return rendered_html