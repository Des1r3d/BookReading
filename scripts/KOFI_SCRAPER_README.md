# Ko-fi Chapter Scraper - Hướng dẫn sử dụng

## Ko-fi Chapter Scraper

Scripts để scrape chapters từ Ko-fi, đặc biệt xử lý Shadow DOM.

## ⚡ PHIÊN BẢN NHANH (Khuyên dùng)

### 1. Python Fast Scraper (`kofi_scraper_fast.py`)

Sử dụng parallel processing, smart wait thay vì sleep cố định:

```bash
# Setup
pip install websockets aiohttp

# Mở Chrome với debugging
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/ChromeDebug"

# Scrape nhiều URLs song song (NHANH NHẤT)
python kofi_scraper_fast.py --urls "url1" "url2" "url3" --parallel 3

# Scrape theo Next Chapter link
python kofi_scraper_fast.py --url "https://ko-fi.com/post/..." --count 5 --delay 300
```

Các tùy chọn:
- `--parallel 3`: Số tabs chạy đồng thời (mặc định: 3)
- `--delay 300`: Delay giữa các batch (ms, mặc định: 500)

### 2. JavaScript Fast Scraper (`kofi_scraper_fast.js`)

Paste vào Console và sử dụng:

```javascript
// Scrape nhiều URLs SONG SONG (nhanh nhất!)
await fastScrape(['url1', 'url2', 'url3'])

// Scrape trang hiện tại và download ngay
await quickScrapeAndDownload()

// Scrape 5 bài theo Next Chapter (delay 500ms)
await fastScrapeChain(5, 500)
```

---

## 📖 PHIÊN BẢN GỐC (Chậm hơn)
Bộ công cụ để scrape chapters từ Ko-fi và chuyển đổi sang format XML phù hợp với hệ thống website đọc truyện.

## Scripts có sẵn

### 1. kofi_scraper.js (Chạy trong Browser Console)
Script JavaScript chạy trực tiếp trong browser, phù hợp cho scraping nhanh.

**Cách sử dụng:**
1. Mở trang Ko-fi chapter trong Chrome (ví dụ: https://ko-fi.com/post/Max-level-priestess-Vol-9-Chapter-137-139-Q5Q61P31NL)
2. Mở Developer Tools (F12)
3. Vào tab Console
4. Copy toàn bộ nội dung file `kofi_scraper.js` và paste vào Console
5. Nhấn Enter

**Các lệnh thường dùng:**
```javascript
// Lấy chapters từ trang hiện tại và xem kết quả
await scrapeChapter()

// Lấy chapters và download file XML ngay
await scrapeAndExport()

// Lấy nhiều bài viết liên tiếp (tự động navigate)
await scrapeMultipleChapters(5)
```

### 2. kofi_scraper_cdp.py (Python với Chrome DevTools Protocol)
Script Python tự động hóa hoàn toàn bằng CDP.

**Yêu cầu:**
```bash
pip install websockets aiohttp
```

**Cách sử dụng:**

1. Mở Chrome với debugging enabled:
```bash
# Windows
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/ChromeDebug"

# hoặc đường dẫn đầy đủ
"C:/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/ChromeDebug"
```

2. Login vào Ko-fi trong Chrome browser vừa mở

3. Chạy script:
```bash
# Scrape 1 bài viết
python kofi_scraper_cdp.py --url "https://ko-fi.com/post/..." --count 1

# Scrape 5 bài viết liên tiếp
python kofi_scraper_cdp.py --url "https://ko-fi.com/post/..." --count 5

# Chỉ định thư mục output
python kofi_scraper_cdp.py --url "https://ko-fi.com/post/..." --count 3 --output "F:/Chapters"
```

**Tham số:**
- `--url, -u`: URL của bài viết đầu tiên (bắt buộc)
- `--count, -c`: Số bài viết cần scrape (mặc định: 1)
- `--output, -o`: Thư mục output (mặc định: Chapters/)
- `--port, -p`: Chrome debugging port (mặc định: 9222)

## Output Format

Các script tạo file XML với format:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<chapters>
  <chapter number="137" volume="9">
    <title>The Strange Loot Has Increased!</title>
    <text>Nội dung chapter...</text>
  </chapter>
  ...
</chapters>
```

File được lưu với tên: `ch{start}_{end}.vn.txt` (ví dụ: `ch137_139.vn.txt`)

## Lưu ý quan trọng

1. **Ko-fi sử dụng Shadow DOM** - Các script đã được cập nhật để xử lý điều này
2. **Cần login** - Một số nội dung yêu cầu đăng nhập Ko-fi
3. **Rate limiting** - Có delay 2 giây giữa các requests để tránh bị chặn
4. **Link ">> Next Chapter"** - Scripts tự động tìm và follow link này

## Workflow đề xuất

1. Mở Chrome với debugging
2. Login vào Ko-fi
3. Dùng Python script để scrape tự động
4. Files được lưu vào thư mục Chapters/
5. Chạy `python parse_chapters.py` để cập nhật website
