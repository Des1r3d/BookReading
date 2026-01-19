"""
Translation Script for Novel Chapters
=====================================
Dịch các chương từ tiếng Anh sang tiếng Việt sử dụng OpenAI API (self-hosted).
Chạy 5 tiến trình song song để tăng tốc độ.

Usage:
    python translate_chapters.py
    
Configuration:
    Điều chỉnh API_BASE_URL, API_KEY, và MODEL_NAME bên dưới trước khi chạy.
"""

import asyncio
import os
import re
from pathlib import Path
from typing import Optional
import aiohttp

# ============================================================================
# CONFIGURATION - Điều chỉnh các giá trị này theo API của bạn
# ============================================================================
API_BASE_URL = "http://localhost:8080/v1"  # URL của OpenAI API self-hosted
API_KEY = "your-api-key"                    # API key (để trống nếu không cần)
MODEL_NAME = "gpt-4"                        # Tên model sử dụng
MAX_CONCURRENT = 5                          # Số tiến trình song song
MAX_RETRIES = 3                             # Số lần retry khi lỗi
# ============================================================================

# Thư mục làm việc
SCRIPT_DIR = Path(__file__).parent
INPUT_DIR = SCRIPT_DIR / "Chapters_Untranslated"
OUTPUT_DIR = SCRIPT_DIR / "Chapters_Translated"

# System prompt với đầy đủ quy tắc dịch thuật
SYSTEM_PROMPT = """Bạn là một biên dịch viên tiểu thuyết Fantasy chuyên nghiệp. Nhiệm vụ của bạn là dịch văn bản sang tiếng Việt, tuân thủ nghiêm ngặt các thiết lập thế giới và nhân vật dưới đây.

### 1. QUY TẮC DỊCH TÊN & THUẬT NGỮ (BẮT BUỘC)

**A. Tên nhân vật:**

1.  **Violet** → Dịch thành **Willis**.

2.  **Light** → Dịch thành **Bé Quang**.

    * *Ngoại lệ:* Nếu "Light" nằm trong Họ tên (Surname) người khác → Giữ nguyên (VD: Mr. Lightman).

3.  **Xiao Guang** → Dịch thành **Tiểu Quang**.



**B. Thuật ngữ cố định (Glossary):**

* Tư tế → **Mục sư**

* Great Era → **Đại Thế**

* Thần vực → **Thần quốc**

* Nữ thần đất → **Đại Địa Mẫu Thần**

* Spirit Veil → **Linh Ẩn**

* Bình Minh → **Hy**

* Nguyên giới → **Khởi Nguyên chi địa**

* Thần tính → **Thần cách**

* Hen → **Ngấn**

* Tử vong linh hồn → **Vong Hồn**

* **Lưu ý:** Tên trang bị, vật phẩm, kỹ năng phải dịch theo âm **Hán Việt** (trang trọng).



### 2. MA TRẬN XƯNG HÔ (QUAN TRỌNG)

Narrator sẽ gọi Willis là cô/ tiểu thư mực sư nào đó theo ngữ cảnh.

Willis và Tiểu Quang và Quang là ba nhân vật rất thân thiết

*Các nhân vật phụ khác:* Dịch linh hoạt theo bối cảnh (Tôi/Cậu, Ta/Ngươi, Ngài...).



### 3. VĂN PHONG & TÍNH CÁCH Willis

* **Phong cách:** Tiểu thuyết phương Tây (Western Fantasy). Câu văn mượt mà, hạn chế từ ngữ quá đậm chất kiếm hiệp trong hội thoại đời thường.

* **Tâm lý Willis:**

    * Thể chất Thần tộc: "Ngoài nóng trong lạnh".

    * **Phản ứng cơ thể:** Có thể sốc, run rẩy, sợ hãi, ngây người.

    * **Nội tâm:** Tuyệt đối bình tĩnh, logic và lạnh lùng. Cảm xúc thể xác không ảnh hưởng đến tư duy.

    * *Yêu cầu:* Tách biệt rõ hai trạng thái này khi dịch đoạn nội tâm và miêu tả ngoại hình.



### 4. YÊU CẦU ĐẦU RA

* Chỉ xuất ra bản dịch tiếng Việt.

* Không thêm bình luận hay giải thích.

* Giữ nguyên format paragraph của văn bản gốc."""


async def translate_with_api(session: aiohttp.ClientSession, text: str) -> Optional[str]:
    """
    Gọi OpenAI API để dịch văn bản.
    
    Args:
        session: aiohttp session
        text: Văn bản cần dịch
        
    Returns:
        Văn bản đã dịch hoặc None nếu lỗi
    """
    headers = {
        "Content-Type": "application/json",
    }
    if API_KEY and API_KEY != "your-api-key":
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Dịch đoạn văn sau sang tiếng Việt:\n\n{text}"}
        ],
        "temperature": 0.3,  # Độ sáng tạo thấp để dịch chính xác hơn
        "max_tokens": 8192,
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            async with session.post(
                f"{API_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 phút timeout
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    print(f"  ⚠️ API error (attempt {attempt + 1}/{MAX_RETRIES}): {response.status} - {error_text[:200]}")
                    
        except asyncio.TimeoutError:
            print(f"  ⚠️ Timeout (attempt {attempt + 1}/{MAX_RETRIES})")
        except Exception as e:
            print(f"  ⚠️ Error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
        
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    return None


async def translate_chapter(
    semaphore: asyncio.Semaphore,
    session: aiohttp.ClientSession,
    input_file: Path,
    output_file: Path
) -> bool:
    """
    Dịch một chapter.
    
    Args:
        semaphore: Semaphore để giới hạn concurrent
        session: aiohttp session
        input_file: File input
        output_file: File output
        
    Returns:
        True nếu thành công, False nếu lỗi
    """
    async with semaphore:
        chapter_name = input_file.stem
        print(f"📖 Đang dịch {chapter_name}...")
        
        try:
            # Đọc file input
            with open(input_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Kiểm tra nếu file đã dịch rồi
            if output_file.exists():
                print(f"  ⏭️ {chapter_name} đã được dịch trước đó, bỏ qua.")
                return True
            
            # Gọi API dịch
            translated = await translate_with_api(session, content)
            
            if translated:
                # Lưu kết quả
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(translated)
                print(f"  ✅ {chapter_name} - Hoàn thành!")
                return True
            else:
                print(f"  ❌ {chapter_name} - Lỗi dịch!")
                return False
                
        except Exception as e:
            print(f"  ❌ {chapter_name} - Lỗi: {e}")
            return False


async def translate_all_chapters():
    """
    Dịch tất cả chapters với 5 tiến trình song song.
    """
    # Tạo thư mục output nếu chưa có
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Lấy danh sách files cần dịch
    input_files = sorted(INPUT_DIR.glob("ch*.txt"))
    
    if not input_files:
        print("❌ Không tìm thấy file nào trong Chapters_Untranslated/")
        return
    
    print(f"🚀 Bắt đầu dịch {len(input_files)} chapters với {MAX_CONCURRENT} tiến trình song song...")
    print(f"📁 Input: {INPUT_DIR}")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"🔗 API: {API_BASE_URL}")
    print("-" * 60)
    
    # Tạo semaphore để giới hạn concurrent
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    # Tạo session và dịch
    async with aiohttp.ClientSession() as session:
        tasks = []
        for input_file in input_files:
            output_file = OUTPUT_DIR / f"{input_file.stem}.vn.txt"
            task = translate_chapter(semaphore, session, input_file, output_file)
            tasks.append(task)
        
        # Chạy tất cả tasks
        results = await asyncio.gather(*tasks)
    
    # Thống kê kết quả
    success = sum(results)
    failed = len(results) - success
    
    print("-" * 60)
    print(f"✨ Hoàn thành!")
    print(f"   ✅ Thành công: {success}/{len(results)}")
    if failed > 0:
        print(f"   ❌ Lỗi: {failed}/{len(results)}")


def main():
    """Entry point."""
    print("=" * 60)
    print("  🌐 Novel Chapter Translation Script")
    print("=" * 60)
    print()
    
    # Kiểm tra thư mục input
    if not INPUT_DIR.exists():
        print(f"❌ Không tìm thấy thư mục: {INPUT_DIR}")
        return
    
    # Chạy async
    asyncio.run(translate_all_chapters())


if __name__ == "__main__":
    main()
