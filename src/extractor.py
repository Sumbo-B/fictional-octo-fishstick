import base64
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def extract_image_urls(html_content, base_url):
    soup = BeautifulSoup(html_content, 'lxml')
    img_tags = soup.find_all('img')

    img_urls = []
    for img in img_tags:
        img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')

        if img_url and img_url.startswith('data:image'):
            img_urls.append(decode_base64_image(img_url))
        elif img_url and "obfuscated" in img_url:
            img_urls.append(decode_obfuscated_url(img_url))
        else:
            full_img_url = get_full_resolution_url(img_url)
            img_urls.append(urljoin(base_url, full_img_url) if full_img_url else urljoin(base_url, img_url))

    return img_urls

def decode_base64_image(data_uri):
    img_format, img_base64 = data_uri.split(';base64,')
    img_data = base64.b64decode(img_base64)
    return img_data

def decode_obfuscated_url(url):
    return url.replace("obfuscated", "real-url-part")

def get_full_resolution_url(thumbnail_url):
    if "thumb" in thumbnail_url:
        return thumbnail_url.replace("thumb", "full")
    if "?" in thumbnail_url:
        return thumbnail_url.split("?")[0]
    return None