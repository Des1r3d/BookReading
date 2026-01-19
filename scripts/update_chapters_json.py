"""
Script cập nhật website - thêm các chương từ thư mục Chapters vào website/data/chapters.json

Cách sử dụng:
    python scripts/update_chapters_json.py [--force]
    
    --force: Ghi đè các chapter đã tồn tại thay vì bỏ qua
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Đường dẫn mặc định
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CHAPTERS_DIR = PROJECT_DIR / "Chapters"
CHAPTERS_JSON = PROJECT_DIR / "website" / "data" / "chapters.json"


def parse_chapter_file(file_path: Path) -> List[Dict]:
    """
    Parse một file chapter và trả về danh sách các chapter trong file.
    
    File có thể chứa một hoặc nhiều chapter (ví dụ: ch157_159.vn.txt chứa 3 chapter)
    """
    chapters = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm tất cả các chapter trong file bằng regex
    chapter_pattern = re.compile(
        r'<chapter\s+number="(\d+)"\s+volume="(\d+)">\s*'
        r'<title>(.*?)</title>\s*'
        r'<text>(.*?)</text>\s*'
        r'</chapter>',
        re.DOTALL
    )
    
    matches = chapter_pattern.findall(content)
    
    for match in matches:
        chapter_num = int(match[0])
        volume = int(match[1])
        title = match[2].strip()
        text = match[3].strip()
        
        # Chuyển đổi text: thay <br/> hoặc nhiều dòng trống bằng \n\n
        # Và loại bỏ khoảng trắng thừa
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        chapters.append({
            "id": chapter_num,
            "volume": volume,
            "title": title,
            "content": text
        })
    
    return chapters


def get_existing_chapters(json_path: Path) -> Dict:
    """
    Đọc file chapters.json hiện tại và trả về dữ liệu.
    """
    if not json_path.exists():
        return {
            "bookTitle": "Max Level Priest",
            "bookTitleVi": "Linh Mục Cấp Tối Đa",
            "totalChapters": 0,
            "chapters": []
        }
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_chapters_json(force: bool = False) -> Tuple[int, int, int]:
    """
    Cập nhật file chapters.json với các chapter từ thư mục Chapters.
    
    Returns:
        Tuple[int, int, int]: (số chapter mới thêm, số chapter đã cập nhật, số chapter bỏ qua)
    """
    # Đọc dữ liệu hiện tại
    data = get_existing_chapters(CHAPTERS_JSON)
    existing_chapters = {ch["id"]: ch for ch in data["chapters"]}
    
    # Tìm tất cả các file chapter
    chapter_files = sorted(CHAPTERS_DIR.glob("*.vn.txt"))
    
    added = 0
    updated = 0
    skipped = 0
    
    for file_path in chapter_files:
        print(f"Đang xử lý: {file_path.name}")
        
        try:
            chapters = parse_chapter_file(file_path)
            
            for chapter in chapters:
                chapter_id = chapter["id"]
                
                if chapter_id in existing_chapters:
                    if force:
                        existing_chapters[chapter_id] = chapter
                        updated += 1
                        print(f"  Đã cập nhật chapter {chapter_id}: {chapter['title']}")
                    else:
                        skipped += 1
                        print(f"  Bỏ qua chapter {chapter_id} (đã tồn tại)")
                else:
                    existing_chapters[chapter_id] = chapter
                    added += 1
                    print(f"  Đã thêm chapter {chapter_id}: {chapter['title']}")
                    
        except Exception as e:
            print(f"  Lỗi khi xử lý file {file_path.name}: {e}")
    
    # Sắp xếp chapters theo id
    sorted_chapters = sorted(existing_chapters.values(), key=lambda x: x["id"])
    
    # Cập nhật data
    data["chapters"] = sorted_chapters
    data["totalChapters"] = len(sorted_chapters)
    
    # Ghi ra file
    CHAPTERS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(CHAPTERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Kết quả ===")
    print(f"Đã thêm mới: {added} chapter")
    print(f"Đã cập nhật: {updated} chapter")
    print(f"Đã bỏ qua: {skipped} chapter")
    print(f"Tổng số chapter: {len(sorted_chapters)}")
    print(f"File đã lưu: {CHAPTERS_JSON}")
    
    return added, updated, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Cập nhật website - thêm các chương từ thư mục Chapters vào chapters.json"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Ghi đè các chapter đã tồn tại thay vì bỏ qua"
    )
    
    args = parser.parse_args()
    
    print(f"Thư mục Chapters: {CHAPTERS_DIR}")
    print(f"File chapters.json: {CHAPTERS_JSON}")
    print(f"Chế độ force: {args.force}")
    print()
    
    if not CHAPTERS_DIR.exists():
        print(f"Lỗi: Thư mục Chapters không tồn tại: {CHAPTERS_DIR}")
        return 1
    
    update_chapters_json(force=args.force)
    return 0


if __name__ == "__main__":
    exit(main())
