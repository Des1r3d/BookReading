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
API_BASE_URL = "api"  # URL của OpenAI API self-hosted
API_KEY = "nonono"                    # API key (để trống nếu không cần)
MODEL_NAME = "gemini-3-flash-preview"                        # Tên model sử dụng
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
    * **Phản ứng cơ thể:** Có thể sốc, run rẩy, sợ hãi, ngây người
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
                f"{API_BASE_URL}chat/completions",
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


def get_translation_status() -> tuple[list[Path], list[Path]]:
    """
    Kiểm tra trạng thái dịch của các chapters.
    
    Returns:
        (pending_files, completed_files): Tuple chứa danh sách file chưa dịch và đã dịch
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    all_files = sorted(INPUT_DIR.glob("ch*.txt"))
    pending = []
    completed = []
    
    for input_file in all_files:
        output_file = OUTPUT_DIR / f"{input_file.stem}.vn.txt"
        if output_file.exists():
            completed.append(input_file)
        else:
            pending.append(input_file)
    
    return pending, completed


def show_translation_status():
    """
    Hiển thị trạng thái dịch của các chapters.
    """
    pending, completed = get_translation_status()
    total = len(pending) + len(completed)
    
    print("=" * 60)
    print("  📊 TRẠNG THÁI DỊCH CHAPTERS")
    print("=" * 60)
    print(f"📁 Input: {INPUT_DIR}")
    print(f"📁 Output: {OUTPUT_DIR}")
    print("-" * 60)
    print(f"✅ Đã dịch: {len(completed)}/{total}")
    print(f"⏳ Chưa dịch: {len(pending)}/{total}")
    
    if pending:
        print("\n📝 Danh sách chưa dịch:")
        for i, f in enumerate(pending[:20], 1):  # Chỉ hiển thị 20 file đầu
            print(f"   {i}. {f.stem}")
        if len(pending) > 20:
            print(f"   ... và {len(pending) - 20} file khác")
    
    print("=" * 60)
    return pending, completed


async def translate_chapter(
    semaphore: asyncio.Semaphore,
    session: aiohttp.ClientSession,
    input_file: Path,
    output_file: Path,
    index: int,
    total: int
) -> bool:
    """
    Dịch một chapter.
    
    Args:
        semaphore: Semaphore để giới hạn concurrent
        session: aiohttp session
        input_file: File input
        output_file: File output
        index: Số thứ tự chapter đang dịch
        total: Tổng số chapters cần dịch
        
    Returns:
        True nếu thành công, False nếu lỗi
    """
    chapter_name = input_file.stem
    
    # Kiểm tra nếu file đã dịch rồi (trước khi acquire semaphore)
    if output_file.exists():
        print(f"  ⏭️ [{index}/{total}] {chapter_name} - Đã dịch trước đó, bỏ qua.")
        return True
    
    async with semaphore:
        print(f"📖 [{index}/{total}] Đang dịch {chapter_name}...")
        
        try:
            # Đọc file input
            with open(input_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Gọi API dịch
            translated = await translate_with_api(session, content)
            
            if translated:
                # Lưu kết quả
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(translated)
                print(f"  ✅ [{index}/{total}] {chapter_name} - Hoàn thành!")
                return True
            else:
                print(f"  ❌ [{index}/{total}] {chapter_name} - Lỗi dịch!")
                return False
                
        except Exception as e:
            print(f"  ❌ [{index}/{total}] {chapter_name} - Lỗi: {e}")
            return False


async def translate_all_chapters():
    """
    Dịch tất cả chapters với 5 tiến trình song song.
    """
    # Kiểm tra trạng thái trước
    pending_files, completed_files = get_translation_status()
    
    if not pending_files and not completed_files:
        print("❌ Không tìm thấy file nào trong Chapters_Untranslated/")
        return
    
    total_all = len(pending_files) + len(completed_files)
    
    print(f"📊 Trạng thái: {len(completed_files)}/{total_all} đã dịch")
    
    if not pending_files:
        print("✨ Tất cả chapters đã được dịch!")
        return
    
    print(f"🚀 Bắt đầu dịch {len(pending_files)} chapters còn lại với {MAX_CONCURRENT} tiến trình song song...")
    print(f"📁 Input: {INPUT_DIR}")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"🔗 API: {API_BASE_URL}")
    print("-" * 60)
    
    # Tạo semaphore để giới hạn concurrent
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    # Tạo session và dịch - CHỈ dịch các file chưa hoàn thành
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, input_file in enumerate(pending_files, 1):
            output_file = OUTPUT_DIR / f"{input_file.stem}.vn.txt"
            task = translate_chapter(semaphore, session, input_file, output_file, i, len(pending_files))
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
