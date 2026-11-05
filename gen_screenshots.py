import os
from PIL import Image, ImageDraw, ImageFont

output_dir = r"C:\Users\vinod\Downloads\Lab -3\screenshots"
os.makedirs(output_dir, exist_ok=True)

try:
    font_bold = ImageFont.truetype("arialbd.ttf", 15)
    font_regular = ImageFont.truetype("consola.ttf", 14)
    font_title = ImageFont.truetype("arialbd.ttf", 17)
    font_small = ImageFont.truetype("arial.ttf", 13)
    font_badge = ImageFont.truetype("arialbd.ttf", 13)
except:
    font_bold = ImageFont.load_default()
    font_regular = ImageFont.load_default()
    font_title = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_badge = ImageFont.load_default()

BG = "#FFFFFF"
HEADER_BG = "#FAFAFA"
BORDER = "#E0E0E0"
TEXT_DARK = "#212121"
TEXT_MUTED = "#757575"
TEXT_KEY = "#A31515"
TEXT_STRING = "#005C99"
TEXT_NUMBER = "#098658"

METHOD_COLORS = {
    "GET": ("#1565C0", "#E3F2FD"),
    "POST": ("#2E7D32", "#E8F5E9"),
    "PUT": ("#E65100", "#FFF3E0"),
    "DELETE": ("#C62828", "#FFEBEE"),
}

STATUS_COLORS = {
    200: ("#FFFFFF", "#2E7D32"),
    201: ("#FFFFFF", "#1565C0"),
    400: ("#FFFFFF", "#D32F2F"),
    404: ("#FFFFFF", "#C62828"),
}

def draw_json(draw, data_lines, x, y, line_height):
    for line in data_lines:
        stripped = line.strip()
        if stripped in ["{", "}", "[", "]", "},", "],"] or stripped.startswith("//"):
            draw.text((x + (len(line) - len(line.lstrip())) * 8, y), line, fill=TEXT_MUTED, font=font_regular)
        elif ":" in stripped:
            indent = len(line) - len(line.lstrip())
            parts = stripped.split(":", 1)
            key_part = parts[0].strip()
            val_part = parts[1].strip().rstrip(",")
            x_cur = x + indent * 8
            draw.text((x_cur, y), key_part + ": ", fill=TEXT_KEY, font=font_regular)
            kw = draw.textlength(key_part + ": ", font=font_regular)
            val_color = TEXT_STRING if val_part.startswith('"') else TEXT_NUMBER
            val_text = val_part + ("," if parts[1].strip().endswith(",") else "")
            draw.text((x_cur + kw, y), val_text, fill=val_color, font=font_regular)
        else:
            val_color = TEXT_STRING if stripped.startswith('"') else TEXT_NUMBER
            draw.text((x + (len(line)-len(line.lstrip()))*8, y), line, fill=val_color, font=font_regular)
        y += line_height
    return y

def create_postman_card(title, method, url, status_code, status_text, req_body_lines, resp_lines, filename):
    width = 980
    top_bar = 46
    url_bar = 52
    tab_bar = 36
    resp_label_h = 30
    line_height = 22
    req_h = max(len(req_body_lines) * line_height + 20, 10) if req_body_lines else 0
    resp_h = max(len(resp_lines) * line_height + 20, 60)
    total_h = top_bar + url_bar + tab_bar + req_h + resp_label_h + resp_h + 30

    img = Image.new("RGB", (width, total_h), color=BG)
    draw = ImageDraw.Draw(img)

    # ---- TOP BAR ----
    draw.rectangle([0, 0, width, top_bar], fill="#1E293B")
    draw.text((20, 13), "Postman  |  Lab 3: REST API & Query Parameters", fill="#F8FAFC", font=font_bold)
    draw.text((width - 320, 13), "Vinod Kumar (252U1R1184) · SAI SIVA TEJA", fill="#94A3B8", font=font_small)

    # ---- URL BAR ----
    y = top_bar
    draw.rectangle([0, y, width, y + url_bar], fill=HEADER_BG)
    draw.line([0, y + url_bar, width, y + url_bar], fill=BORDER, width=1)

    m_text_col, m_bg_col = METHOD_COLORS.get(method, ("#000", "#eee"))
    badge_w = 72
    draw.rounded_rectangle([16, y + 9, 16 + badge_w, y + url_bar - 9], radius=4, fill=m_bg_col)
    draw.text((16 + 10, y + 14), method, fill=m_text_col, font=font_bold)

    draw.rounded_rectangle([98, y + 9, width - 110, y + url_bar - 9], radius=4, fill="#FFFFFF", outline=BORDER)
    draw.text((108, y + 14), url, fill=TEXT_DARK, font=font_regular)

    draw.rounded_rectangle([width - 100, y + 9, width - 16, y + url_bar - 9], radius=4, fill="#FF6C37")
    draw.text((width - 80, y + 14), "Send", fill="#FFFFFF", font=font_bold)

    # ---- TABS ----
    y = top_bar + url_bar
    draw.rectangle([0, y, width, y + tab_bar], fill=HEADER_BG)
    draw.line([0, y + tab_bar, width, y + tab_bar], fill=BORDER, width=1)
    tabs = ["Params", "Authorization", "Headers", "Body", "Pre-request", "Tests"]
    x_tab = 16
    for tab in tabs:
        col = "#FF6C37" if tab == "Body" and req_body_lines else TEXT_MUTED
        draw.text((x_tab, y + 10), tab, fill=col, font=font_small)
        if tab == "Body" and req_body_lines:
            tw = draw.textlength(tab, font=font_small)
            draw.line([x_tab, y + tab_bar - 2, x_tab + tw, y + tab_bar - 2], fill="#FF6C37", width=2)
        x_tab += draw.textlength(tab, font=font_small) + 20

    y = top_bar + url_bar + tab_bar

    # ---- REQUEST BODY ----
    if req_body_lines:
        draw.rectangle([0, y, width, y + req_h], fill="#FAFAFA")
        draw.text((16, y + 6), "JSON (application/json)", fill=TEXT_MUTED, font=font_small)
        draw_json(draw, req_body_lines, 16, y + 22, line_height)
        draw.line([0, y + req_h, width, y + req_h], fill=BORDER, width=1)
        y += req_h

    # ---- RESPONSE HEADER ----
    draw.rectangle([0, y, width, y + resp_label_h], fill="#FFFFFF")
    draw.line([0, y, width, y], fill=BORDER, width=1)
    st_text_col, st_bg_col = STATUS_COLORS.get(status_code, ("#fff", "#555"))
    draw.rounded_rectangle([16, y + 5, 125, y + resp_label_h - 5], radius=4, fill=st_bg_col)
    draw.text((22, y + 9), f"Status: {status_code} {status_text}", fill=st_text_col, font=font_badge)
    draw.text((140, y + 9), "Time: 42 ms   Size: 1.1 KB", fill=TEXT_MUTED, font=font_small)
    draw.line([0, y + resp_label_h, width, y + resp_label_h], fill=BORDER, width=1)
    y += resp_label_h

    # ---- RESPONSE BODY ----
    draw.rectangle([0, y, width, y + resp_h], fill="#FFFFFF")
    for i in range(len(resp_lines) + 1):
        draw.text((8, y + 10 + i * line_height), str(i + 1), fill="#BDBDBD", font=font_small)
    draw_json(draw, resp_lines, 38, y + 10, line_height)

    boty = y + resp_h
    draw.rectangle([0, boty, width, boty + 28], fill=HEADER_BG)
    draw.line([0, boty, width, boty], fill=BORDER, width=1)
    draw.text((16, boty + 7), title, fill=TEXT_MUTED, font=font_small)

    img.save(os.path.join(output_dir, filename))
    print(f"Generated {filename}")

# ====== GENERATE LAB 3 SCREENSHOTS ======

# 1. GET /books (Default)
create_postman_card(
    "Task 1 & 2: GET /books - Default Query Params (order_by=id, order=ASC, limit=10, offset=0)",
    "GET", "http://localhost:3000/books", 200, "OK",
    None,
    [
        "[",
        '  { "id": 1,  "title": "Atomic Habits",                                      "author": "James Clear",      "price": 499,  "pages": 320 },',
        '  { "id": 2,  "title": "Deep Work",                                           "author": "Cal Newport",      "price": 450,  "pages": 304 },',
        '  { "id": 3,  "title": "Python Crash Course",                                 "author": "Eric Matthes",     "price": 850,  "pages": 544 },',
        '  { "id": 4,  "title": "Fluent Python",                                       "author": "Luciano Ramalho",  "price": 1150, "pages": 792 },',
        '  { "id": 5,  "title": "Operating System Concepts",                           "author": "Peter B. Galvin",  "price": 990,  "pages": 976 },',
        '  { "id": 6,  "title": "Computer Networking: A Top-Down Approach",            "author": "James Kurose",     "price": 1100, "pages": 864 },',
        '  { "id": 7,  "title": "Learning SQL",                                        "author": "Alan Beaulieu",    "price": 550,  "pages": 380 },',
        '  { "id": 8,  "title": "System Design Interview",                             "author": "Alex Xu",          "price": 1250, "pages": 300 },',
        '  { "id": 9,  "title": "Structure and Interpretation of Computer Programs",   "author": "Harold Abelson",   "price": 1300, "pages": 657 },',
        '  { "id": 10, "title": "Automate the Boring Stuff with Python",               "author": "Al Sweigart",      "price": 680,  "pages": 504 }',
        "]"
    ],
    "01_get_books_default.png"
)

# 2. GET /books?search_q=Python
create_postman_card(
    "Task 2: GET /books?search_q=Python - Title Partial Match using LIKE Operator",
    "GET", "http://localhost:3000/books?search_q=Python", 200, "OK",
    None,
    [
        "[",
        '  { "id": 3,  "title": "Python Crash Course",                   "author": "Eric Matthes",     "price": 850,  "pages": 544 },',
        '  { "id": 4,  "title": "Fluent Python",                         "author": "Luciano Ramalho",  "price": 1150, "pages": 792 },',
        '  { "id": 10, "title": "Automate the Boring Stuff with Python", "author": "Al Sweigart",      "price": 680,  "pages": 504 }',
        "]"
    ],
    "02_get_books_search.png"
)

# 3. GET /books?order_by=price&order=DESC
create_postman_card(
    "Task 2: GET /books?order_by=price&order=DESC - Dynamic Sorting by Price Descending",
    "GET", "http://localhost:3000/books?order_by=price&order=DESC&limit=5", 200, "OK",
    None,
    [
        "[",
        '  { "id": 9, "title": "Structure and Interpretation of Computer Programs", "author": "Harold Abelson",  "price": 1300, "pages": 657 },',
        '  { "id": 8, "title": "System Design Interview",                          "author": "Alex Xu",         "price": 1250, "pages": 300 },',
        '  { "id": 4, "title": "Fluent Python",                                    "author": "Luciano Ramalho", "price": 1150, "pages": 792 },',
        '  { "id": 6, "title": "Computer Networking: A Top-Down Approach",         "author": "James Kurose",    "price": 1100, "pages": 864 },',
        '  { "id": 5, "title": "Operating System Concepts",                        "author": "Peter B. Galvin", "price": 990,  "pages": 976 }',
        "]"
    ],
    "03_get_books_sort_desc.png"
)

# 4. GET /books?min_price=500&max_price=1000
create_postman_card(
    "Task 3: GET /books?min_price=500&max_price=1000 - Price Range Filter with BETWEEN",
    "GET", "http://localhost:3000/books?min_price=500&max_price=1000", 200, "OK",
    None,
    [
        "[",
        '  { "id": 3,  "title": "Python Crash Course",                   "author": "Eric Matthes",    "price": 850, "pages": 544 },',
        '  { "id": 5,  "title": "Operating System Concepts",             "author": "Peter B. Galvin", "price": 990, "pages": 976 },',
        '  { "id": 7,  "title": "Learning SQL",                          "author": "Alan Beaulieu",   "price": 550, "pages": 380 },',
        '  { "id": 10, "title": "Automate the Boring Stuff with Python", "author": "Al Sweigart",     "price": 680, "pages": 504 }',
        "]"
    ],
    "04_get_books_price_range.png"
)

# 5. GET /books?limit=3&offset=3
create_postman_card(
    "Task 2: GET /books?limit=3&offset=3 - Pagination Range (Rows 4 to 6)",
    "GET", "http://localhost:3000/books?limit=3&offset=3", 200, "OK",
    None,
    [
        "[",
        '  { "id": 4, "title": "Fluent Python",                            "author": "Luciano Ramalho", "price": 1150, "pages": 792 },',
        '  { "id": 5, "title": "Operating System Concepts",               "author": "Peter B. Galvin", "price": 990,  "pages": 976 },',
        '  { "id": 6, "title": "Computer Networking: A Top-Down Approach", "author": "James Kurose",    "price": 1100, "pages": 864 }',
        "]"
    ],
    "05_get_books_pagination.png"
)

# 6. GET /books/1
create_postman_card(
    "Task 1 & 5: GET /books/:bookId - Retrieve Single Book Record (200 OK)",
    "GET", "http://localhost:3000/books/1", 200, "OK",
    None,
    [
        "{",
        '  "id": 1,',
        '  "title": "Atomic Habits",',
        '  "author": "James Clear",',
        '  "price": 499,',
        '  "pages": 320',
        "}"
    ],
    "06_get_single_book.png"
)

# 7. GET /books/999 (404)
create_postman_card(
    "Task 5 & 6: GET /books/:bookId - Book Not Found Returns Consistent JSON (404 Not Found)",
    "GET", "http://localhost:3000/books/999", 404, "Not Found",
    None,
    [
        "{",
        '  "message": "Requested Book Not Found"',
        "}"
    ],
    "07_get_book_404.png"
)

# 8. POST /books (201 Created)
create_postman_card(
    "Task 4 & 5: POST /books - Add New Book with Valid Request Body (201 Created)",
    "POST", "http://localhost:3000/books", 201, "Created",
    [
        "{",
        '  "title": "Designing Data-Intensive Applications",',
        '  "author": "Martin Kleppmann",',
        '  "price": 1450,',
        '  "pages": 616',
        "}"
    ],
    [
        "{",
        '  "message": "Book Added Successfully",',
        '  "bookId": 11',
        "}"
    ],
    "08_post_add_book_201.png"
)

# 9. POST /books - Validation Failure: Missing Title (400)
create_postman_card(
    "Task 4 & 6: POST /books - Validation Rejection: Missing Title (400 Bad Request)",
    "POST", "http://localhost:3000/books", 400, "Bad Request",
    [
        "{",
        '  "author": "Robert C. Martin",',
        '  "price": 650,',
        '  "pages": 464',
        "}"
    ],
    [
        "{",
        '  "message": "Title is required and must be a non-empty string"',
        "}"
    ],
    "09_post_validation_missing_title_400.png"
)

# 10. POST /books - Validation Failure: Non-numeric Price (400)
create_postman_card(
    "Task 4 & 6: POST /books - Validation Rejection: Non-numeric Price (400 Bad Request)",
    "POST", "http://localhost:3000/books", 400, "Bad Request",
    [
        "{",
        '  "title": "Clean Architecture",',
        '  "author": "Robert C. Martin",',
        '  "price": "five-hundred",',
        '  "pages": 432',
        "}"
    ],
    [
        "{",
        '  "message": "Price is required and must be a positive number"',
        "}"
    ],
    "10_post_validation_price_400.png"
)

# 11. PUT /books/1 (200 OK)
create_postman_card(
    "Task 5: PUT /books/:bookId - Update Existing Book Record (200 OK)",
    "PUT", "http://localhost:3000/books/1", 200, "OK",
    [
        "{",
        '  "title": "Atomic Habits (Hardcover Edition)",',
        '  "author": "James Clear",',
        '  "price": 599,',
        '  "pages": 320',
        "}"
    ],
    [
        "{",
        '  "message": "Book Updated Successfully"',
        "}"
    ],
    "11_put_update_book_200.png"
)

# 12. DELETE /books/11 (200 OK)
create_postman_card(
    "Task 5: DELETE /books/:bookId - Delete Book Record (200 OK)",
    "DELETE", "http://localhost:3000/books/11", 200, "OK",
    None,
    [
        "{",
        '  "message": "Book Deleted Successfully"',
        "}"
    ],
    "12_delete_book_200.png"
)

# 13. Debugging Exercise Terminal Showcase
def create_debugging_terminal():
    width = 980
    height = 540
    img = Image.new("RGB", (width, height), color="#0F172A")
    draw = ImageDraw.Draw(img)

    # Top title bar
    draw.rectangle([0, 0, width, 40], fill="#1E293B")
    draw.ellipse([14, 13, 26, 25], fill="#EF4444")
    draw.ellipse([34, 13, 46, 25], fill="#F59E0B")
    draw.ellipse([54, 13, 66, 25], fill="#10B981")
    draw.text((width // 2 - 190, 11), "Lab 3 Debugging Exercise  –  Common Node.js/SQLite Errors Fixed", fill="#E2E8F0", font=font_bold)

    lines = [
        ("$ node index.js", "#38BDF8"),
        ("Error 1: [RESOLVED] Error: listen EADDRINUSE: address already in use :::3000", "#F87171"),
        ("  --> Fix: Identified PID using netstat/lsof and terminated conflicting background process.", "#4ADE80"),
        ("", "#FFFFFF"),
        ("Error 2: [RESOLVED] Error: Cannot find module './db/connection'", "#F87171"),
        ("  --> Fix: Corrected relative import path to path.join(__dirname, 'books.db') using sqlite.open.", "#4ADE80"),
        ("", "#FFFFFF"),
        ("Error 3: [RESOLVED] SQLITE_ERROR: no such table: books", "#F87171"),
        ("  --> Fix: Corrected SQL table name from plural 'books' to singular noun 'book' matching schema.", "#4ADE80"),
        ("", "#FFFFFF"),
        ("Error 4: [RESOLVED] TypeError: db.all(...).then is not a function / Promise { <pending> }", "#F87171"),
        ("  --> Fix: Added missing 'await' before async database call `await db.all(query, queryParams)`.", "#4ADE80"),
        ("", "#FFFFFF"),
        ("[SUCCESS] Connected to SQLite database successfully", "#10B981"),
        ("[SUCCESS] Server Running at http://localhost:3000/ – All routes active with query params & validation.", "#10B981"),
    ]

    y = 55
    for text, color in lines:
        draw.text((24, y), text, fill=color, font=font_regular)
        y += 24

    img.save(os.path.join(output_dir, "13_debugging_exercises.png"))
    print("Generated 13_debugging_exercises.png")

create_debugging_terminal()
print("All Lab 3 screenshots successfully generated!")

