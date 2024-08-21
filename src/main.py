from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.fetcher import fetch_page, fetch_dynamic_page, fetch_infinite_scroll_page, is_page_static
from src.extractor import extract_image_urls
from src.utils import save_image, setup_logger, create_images_folder
import os

# Initialize the FastAPI app
app = FastAPI()

# Set up logger and ensure images folder exists
logger = setup_logger()
create_images_folder()

# Define the request model for the scraper
class ScrapeRequest(BaseModel):
    url: str
    dynamic: bool = False
    infinite_scroll: bool = False
    paginate: bool = False
    start_page: int = 1
    end_page: int = 1

@app.post("/scrape/")
async def scrape_images(request: ScrapeRequest):
    try:
        if request.infinite_scroll:
            html_content = fetch_infinite_scroll_page(request.url)
        elif request.paginate:
            for page in range(request.start_page, request.end_page + 1):
                url = f"{request.url}?page={page}"
                html_content = fetch_dynamic_page(url) if request.dynamic else fetch_page(url)
                if not html_content:
                    continue
                img_urls = extract_image_urls(html_content, request.url)
                for img_url in img_urls:
                    save_image(img_url, logger)
        else:
            if is_page_static(request.url):
                html_content = fetch_page(request.url)
            else:
                html_content = fetch_dynamic_page(request.url)
            if not html_content:
                raise HTTPException(status_code=404, detail="Failed to fetch content")
            img_urls = extract_image_urls(html_content, request.url)
            for img_url in img_urls:
                save_image(img_url, logger)
        return {"status": "success", "message": "Images scraped successfully!"}
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Image Scraper API"}