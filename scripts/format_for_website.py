"""
Format Translated Chapters for Website
=======================================
Chuyển đổi các chapter đã dịch sang định dạng XML cho website.

Usage:
    python format_for_website.py
    
Input:
    Chapters_Translated/*.vn.txt
    
Output:
    ../Chapters/chXXX.vn.txt (định dạng XML)
"""

import re
import os
from pathlib import Path
from typing import Tuple, Optional

# Thư mục làm việc
SCRIPT_DIR = Path(__file__).parent
INPUT_DIR = SCRIPT_DIR / "Chapters_Translated"
OUTPUT_DIR = SCRIPT_DIR.parent / "Chapters"

# Mapping chapter number to volume (điều chỉnh theo truyện của bạn)
# Format: (start_chapter, end_chapter, volume_number)
VOLUME_MAPPING = [
    (1, 30, 1),
    (31, 60, 2),
    (61, 90, 3),
    (91, 120, 4),
    (121, 150, 5),
    (151, 180, 6),
    (181, 210, 7),
    (211, 240, 8),
    (241, 270, 9),
    (271, 300, 10),
    (301, 330, 11),
    (331, 360, 12),
]


def get_volume(chapter_num: int) -> int:
    """
    Lấy volume number từ chapter number.
    
    Args:
        chapter_num: Số chapter
        
    Returns:
        Volume number
    """
    for start, end, volume in VOLUME_MAPPING:
        if start <= chapter_num <= end:
            return volume
    # Mặc định nếu không tìm thấy
    return (chapter_num - 1) // 30 + 1


def parse_chapter_content(content: str, chapter_num: int) -> Tuple[str, str]:
    """
    Parse nội dung chapter để lấy title và text.
    
    Args:
        content: Nội dung file đã dịch
        chapter_num: Số chapter
        
    Returns:
        Tuple (title, text)
    """
    lines = content.strip().split('\n')
    
    title = ""
    text_start = 0
    
    # Tìm title từ dòng đầu tiên
    # Format có thể là: "Chương XXX: Title" hoặc "Chapter XXX: Title"
    first_line = lines[0].strip() if lines else ""
    
    # Pattern để match title
    patterns = [
        r'^Chương\s*\d+\s*[:\-]\s*(.+)$',
        r'^Chapter\s*\d+\s*[:\-]\s*(.+)$',
        r'^[Cc]h[aư]ơn?g?\s*\d+\s*[:\-]\s*(.+)$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, first_line, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            text_start = 1
            break
    
    # Nếu không match, dùng dòng đầu làm title
    if not title and first_line:
        # Kiểm tra xem dòng đầu có giống title không
        if len(first_line) < 100 and not first_line.endswith('.'):
            title = first_line
            text_start = 1
        else:
            title = f"Chương {chapter_num}"
    
    # Lấy phần text còn lại
    text_lines = lines[text_start:]
    
    # Bỏ các dòng trống ở đầu
    while text_lines and not text_lines[0].strip():
        text_lines.pop(0)
    
    text = '\n'.join(text_lines)
    
    return title, text


def format_chapter_xml(chapter_num: int, volume: int, title: str, text: str, source_file: str) -> str:
    """
    Format chapter thành XML.
    
    Args:
        chapter_num: Số chapter
        volume: Số volume
        title: Tiêu đề chapter
        text: Nội dung chapter
        source_file: Tên file nguồn
        
    Returns:
        Nội dung XML
    """
    xml_content = f"""<document>
<metadata>
<type>novel_chapters</type>
<volume>{volume}</volume>
<chapters>{chapter_num}</chapters>
<source_file>{source_file}</source_file>
</metadata>

<content>
<chapter number="{chapter_num}" volume="{volume}">
<title>{title}</title>
<text>
{text}
</text>
</chapter>
</content>
</document>"""
    
    return xml_content


def format_chapter(input_file: Path, output_file: Path) -> bool:
    """
    Format một chapter.
    
    Args:
        input_file: File input (đã dịch)
        output_file: File output (XML)
        
    Returns:
        True nếu thành công
    """
    try:
        # Lấy chapter number từ tên file
        match = re.search(r'ch(\d+)', input_file.stem)
        if not match:
            print(f"  ⚠️ Không thể parse chapter number từ: {input_file.name}")
            return False
        
        chapter_num = int(match.group(1))
        volume = get_volume(chapter_num)
        
        # Đọc nội dung
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse title và text
        title, text = parse_chapter_content(content, chapter_num)
        
        # Format XML
        xml_content = format_chapter_xml(
            chapter_num=chapter_num,
            volume=volume,
            title=title,
            text=text,
            source_file=f"ch{chapter_num}.txt"
        )
        
        # Lưu file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_content)
        
        print(f"  ✅ ch{chapter_num} - {title[:30]}{'...' if len(title) > 30 else ''}")
        return True
        
    except Exception as e:
        print(f"  ❌ {input_file.name} - Lỗi: {e}")
        return False


def format_all_chapters():
    """
    Format tất cả chapters đã dịch.
    """
    # Tạo thư mục output nếu chưa có
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Lấy danh sách files
    input_files = sorted(INPUT_DIR.glob("*.vn.txt"))
    
    if not input_files:
        print("❌ Không tìm thấy file nào trong Chapters_Translated/")
        print("   Hãy chạy translate_chapters.py trước!")
        return
    
    print(f"📄 Format {len(input_files)} chapters sang XML...")
    print(f"📁 Input: {INPUT_DIR}")
    print(f"📁 Output: {OUTPUT_DIR}")
    print("-" * 60)
    
    success = 0
    for input_file in input_files:
        # Tạo tên file output (giữ format .vn.txt)
        output_name = input_file.stem.replace('.vn', '') + ".vn.txt"
        output_file = OUTPUT_DIR / output_name
        
        if format_chapter(input_file, output_file):
            success += 1
    
    print("-" * 60)
    print(f"✨ Hoàn thành! {success}/{len(input_files)} files")


def main():
    """Entry point."""
    print("=" * 60)
    print("  📄 Format Chapters for Website")
    print("=" * 60)
    print()
    
    # Kiểm tra thư mục input
    if not INPUT_DIR.exists():
        print(f"❌ Không tìm thấy thư mục: {INPUT_DIR}")
        print("   Hãy chạy translate_chapters.py trước để dịch chapters!")
        return
    
    format_all_chapters()


if __name__ == "__main__":
    main()
