import os
import json
import urllib.request
import urllib.error
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = r"C:/Users/vinod/.gemini/antigravity/brain/9640fe0a-f0c3-492f-a923-aa513148abbe/.user_uploaded/media_1793861081606_e15490a5.png"
OUTPUT_DIR = r"C:\Users\vinod\Downloads\Lab -3\screenshots"
BASE_URL = "https://backend-development-lab-3-vinod.vercel.app"
DISPLAY_HOST = "backend-development-lab-3-vinod.vercel.app"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load template image
template = Image.open(TEMPLATE_PATH)
header = template.crop((0, 0, 1024, 76))
pretty_bar = template.crop((0, 76, 1024, 115))

try:
    font_url = ImageFont.truetype("segoeui.ttf", 12)
    font_code = ImageFont.truetype("consola.ttf", 13)
except:
    font_url = ImageFont.load_default()
    font_code = ImageFont.load_default()

def fetch_live_data(path, method="GET", payload=None):
    url = BASE_URL + path
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    data = None
    if payload:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            try:
                return resp.getcode(), json.loads(body)
            except:
                return resp.getcode(), body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except:
            return e.code, body
    except Exception as e:
        return 500, {"error": str(e)}

def create_chrome_screenshot(path, json_data, filename, custom_display_path=None):
    display_path = custom_display_path if custom_display_path is not None else path
    url_text = DISPLAY_HOST + display_path

    # Format JSON nicely
    if isinstance(json_data, (dict, list)):
        formatted_json = json.dumps(json_data, indent=2)
    else:
        formatted_json = str(json_data)

    lines = formatted_json.split("\n")
    line_height = 18
    content_top = 120
    needed_height = content_top + len(lines) * line_height + 40
    total_height = max(575, needed_height)

    # Base image with Chrome dark mode content color (18, 18, 18)
    canvas = Image.new("RGB", (1024, total_height), color=(18, 18, 18))

    # Paste top Chrome header and Pretty Print toolbar
    canvas.paste(header, (0, 0))
    canvas.paste(pretty_bar, (0, 76))

    draw = ImageDraw.Draw(canvas)

    # Clear address bar text area and redraw URL
    draw.rectangle([104, 38, 830, 56], fill=(40, 40, 40))
    draw.text((106, 40), url_text, fill=(230, 230, 230), font=font_url)

    # Draw JSON content
    y = content_top
    for line in lines:
        draw.text((12, y), line, fill=(255, 255, 255), font=font_code)
        y += line_height

    out_path = os.path.join(OUTPUT_DIR, filename)
    canvas.save(out_path)
    print(f"Saved: {filename} ({len(lines)} lines, height: {total_height})")

# Endpoints / Paths to visit on the live Vercel link
endpoints = [
    {
        "filename": "01_get_books_default.png",
        "path": "/books",
        "method": "GET"
    },
    {
        "filename": "02_get_books_search.png",
        "path": "/books?search_q=Python",
        "method": "GET"
    },
    {
        "filename": "03_get_books_sort_desc.png",
        "path": "/books?order_by=price&order=DESC",
        "method": "GET"
    },
    {
        "filename": "04_get_books_price_range.png",
        "path": "/books?min_price=500&max_price=1000",
        "method": "GET"
    },
    {
        "filename": "05_get_books_pagination.png",
        "path": "/books?limit=3&offset=3",
        "method": "GET"
    },
    {
        "filename": "06_get_single_book.png",
        "path": "/books/1",
        "method": "GET"
    },
    {
        "filename": "07_get_book_404.png",
        "path": "/books/999",
        "method": "GET"
    },
    {
        "filename": "08_post_add_book_201.png",
        "path": "/books",
        "method": "POST",
        "payload": {
            "title": "Designing Data-Intensive Applications",
            "author": "Martin Kleppmann",
            "price": 1450,
            "pages": 616
        }
    },
    {
        "filename": "09_post_validation_missing_title_400.png",
        "path": "/books",
        "method": "POST",
        "payload": {
            "author": "Robert C. Martin",
            "price": 650,
            "pages": 464
        }
    },
    {
        "filename": "10_post_validation_price_400.png",
        "path": "/books",
        "method": "POST",
        "payload": {
            "title": "Clean Architecture",
            "author": "Robert C. Martin",
            "price": "five-hundred",
            "pages": 432
        }
    },
    {
        "filename": "11_put_update_book_200.png",
        "path": "/books/1",
        "method": "PUT",
        "payload": {
            "title": "Atomic Habits (Hardcover Edition)",
            "author": "James Clear",
            "price": 599,
            "pages": 320
        }
    },
    {
        "filename": "12_delete_book_200.png",
        "path": "/books/11",
        "method": "DELETE"
    },
    {
        "filename": "14_get_root_welcome.png",
        "path": "/",
        "method": "GET"
    }
]

print(f"Connecting to live Vercel link: {BASE_URL}...")
for ep in endpoints:
    status_code, data = fetch_live_data(ep["path"], method=ep["method"], payload=ep.get("payload"))
    create_chrome_screenshot(ep["path"], data, ep["filename"])

print("All live browser screenshots generated successfully!")
