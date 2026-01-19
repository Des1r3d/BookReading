"""
Auto Scrape - Tự động kiểm tra và scrape chapters mới

Script này sẽ:
1. Quét folder Chapters_Untranslated để tìm chapter cao nhất đã có
2. Tự động scrape đến chapter mới nhất (hoặc theo target)
3. Lưu vào folder Chapters_Untranslated

Cách sử dụng:
    # Tự động scrape TẤT CẢ chapters mới (đến khi hết)
    python auto_scrape.py --auto --url "https://ko-fi.com/post/..."
    
    # Chỉ định chapter đích
    python auto_scrape.py --target 270 --url "..."
    
    # Chỉ định số bài viết
    python auto_scrape.py --count 5 --url "..."
    
    # Xem trạng thái
    python auto_scrape.py --status
"""

import os
import re
import sys
import argparse
from pathlib import Path

# Import từ kofi_scraper_fast
try:
    from kofi_scraper_fast import FastKofiScraper, parse_chapters_from_content, format_to_xml
    import asyncio
except ImportError:
    print("❌ Không thể import kofi_scraper_fast. Đảm bảo file nằm cùng thư mục.")
    sys.exit(1)


# Cấu hình
CHAPTERS_DIR = Path(__file__).parent / "Chapters_Untranslated"
# Base URL pattern cho Ko-fi posts (cần điền đúng author)
KOFI_AUTHOR = "your_kofi_author"  # Thay đổi nếu cần


def save_chapters_separately(chapters: list, output_dir: Path = None) -> list:
    """
    Lưu từng chapter vào file riêng biệt.
    
    Args:
        chapters: List các chapter dict với keys: id, title, content
        output_dir: Thư mục lưu file (mặc định: CHAPTERS_DIR)
    
    Returns:
        Danh sách các đường dẫn file đã tạo
    """
    if not chapters:
        return []
    
    if output_dir is None:
        output_dir = CHAPTERS_DIR
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    for chapter in chapters:
        ch_id = chapter['id']
        filename = f"ch{ch_id}.txt"
        output_path = output_dir / filename
        
        # Format single chapter to XML
        xml_content = format_to_xml([chapter])
        output_path.write_text(xml_content, encoding='utf-8')
        
        saved_files.append(output_path)
        print(f"   💾 Đã lưu: {filename}")
    
    return saved_files


def get_latest_chapter() -> int:
    """Quét folder và trả về số chapter cao nhất đã có"""
    if not CHAPTERS_DIR.exists():
        print(f"⚠️ Folder {CHAPTERS_DIR} không tồn tại. Tạo mới...")
        CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
        return 0
    
    max_chapter = 0
    chapter_files = list(CHAPTERS_DIR.glob("ch*.txt"))
    
    for file in chapter_files:
        # Parse filename: ch255_257.txt hoặc ch258.txt
        match = re.match(r'ch(\d+)(?:_(\d+))?\.txt', file.name)
        if match:
            start_ch = int(match.group(1))
            end_ch = int(match.group(2)) if match.group(2) else start_ch
            max_chapter = max(max_chapter, end_ch)
    
    return max_chapter


def get_chapter_summary() -> dict:
    """Trả về thông tin tổng hợp về các chapters đã có"""
    if not CHAPTERS_DIR.exists():
        return {"files": [], "total_chapters": 0, "latest": 0, "gaps": []}
    
    files = []
    all_chapters = set()
    
    for file in sorted(CHAPTERS_DIR.glob("ch*.txt")):
        match = re.match(r'ch(\d+)(?:_(\d+))?\.txt', file.name)
        if match:
            start_ch = int(match.group(1))
            end_ch = int(match.group(2)) if match.group(2) else start_ch
            files.append({
                "name": file.name,
                "start": start_ch,
                "end": end_ch,
                "size": file.stat().st_size
            })
            for ch in range(start_ch, end_ch + 1):
                all_chapters.add(ch)
    
    # Tìm gaps (chapters bị thiếu)
    gaps = []
    if all_chapters:
        min_ch = min(all_chapters)
        max_ch = max(all_chapters)
        for ch in range(min_ch, max_ch + 1):
            if ch not in all_chapters:
                gaps.append(ch)
    
    return {
        "files": files,
        "total_chapters": len(all_chapters),
        "latest": max(all_chapters) if all_chapters else 0,
        "gaps": gaps
    }


def print_status():
    """In trạng thái hiện tại của chapters"""
    summary = get_chapter_summary()
    
    print("\n" + "=" * 60)
    print("📚 TRẠNG THÁI CHAPTERS")
    print("=" * 60)
    
    if not summary["files"]:
        print("   Chưa có chapter nào trong folder.")
    else:
        print(f"\n📁 Folder: {CHAPTERS_DIR}")
        print(f"\n📖 Files hiện có:")
        for f in summary["files"]:
            size_kb = f["size"] / 1024
            print(f"   • {f['name']} (Ch.{f['start']}-{f['end']}) - {size_kb:.1f}KB")
        
        print(f"\n📊 Tổng hợp:")
        print(f"   • Tổng số chapters: {summary['total_chapters']}")
        print(f"   • Chapter mới nhất: {summary['latest']}")
        
        if summary["gaps"]:
            print(f"   • ⚠️ Chapters bị thiếu: {summary['gaps']}")
    
    print("=" * 60)
    return summary


async def scrape_new_chapters(start_url: str, count: int, delay_ms: int = 500):
    """Scrape chapters mới sử dụng FastKofiScraper"""
    scraper = FastKofiScraper(
        debug_port=9222,
        parallel_tabs=1,  # Sequential để follow Next Chapter link
        delay_ms=delay_ms
    )
    
    chapters = await scraper.scrape_sequential_with_next(start_url, count)
    
    if chapters:
        saved_files = save_chapters_separately(chapters, CHAPTERS_DIR)
        return chapters, saved_files
    
    return [], []


async def scrape_until_end(start_url: str, delay_ms: int = 500, max_posts: int = 50):
    """
    Tự động scrape TẤT CẢ chapters mới cho đến khi hết Next Chapter link.
    
    Args:
        start_url: URL bắt đầu
        delay_ms: Delay giữa các request
        max_posts: Giới hạn số bài tối đa để tránh loop vô hạn (mặc định: 50)
    """
    scraper = FastKofiScraper(
        debug_port=9222,
        parallel_tabs=1,
        delay_ms=delay_ms
    )
    
    all_chapters = []
    current_url = start_url
    post_count = 0
    
    # Lấy tab hiện có
    tabs = await scraper.get_tabs()
    kofi_tab = None
    for tab in tabs:
        if tab.get('type') == 'page':
            kofi_tab = tab
            break
    
    if not kofi_tab:
        raise Exception("Không tìm thấy tab Chrome nào")
    
    tab_id = kofi_tab['id']
    
    try:
        await scraper.connect_to_tab(kofi_tab)
        
        while current_url and post_count < max_posts:
            post_count += 1
            print(f"\n📖 [Bài {post_count}] Scraping: {current_url[:60]}...")
            
            # Navigate và đợi
            loaded = await scraper.navigate_and_wait(tab_id, current_url)
            if not loaded:
                print("   ⚠️ Page load timeout, thử extract anyway...")
            
            # Extract
            data = await scraper.extract_chapter_from_tab(tab_id)
            chapters = parse_chapters_from_content(data['content'], data['title'])
            
            all_chapters.extend(chapters)
            
            for ch in chapters:
                print(f"   ✅ Chapter {ch['id']}: {ch['title'][:40]}...")
            
            # Tìm Next URL
            next_url = data.get('nextChapterUrl')
            
            if next_url and next_url != current_url:
                current_url = next_url
                await asyncio.sleep(delay_ms / 1000)
            else:
                print("\n🏁 Đã đến chapter mới nhất! (Không có Next Chapter link)")
                break
                
    finally:
        if tab_id in scraper.sessions:
            await scraper.sessions[tab_id]['ws'].close()
    
    # Lưu từng chapter vào file riêng
    if all_chapters:
        saved_files = save_chapters_separately(all_chapters, CHAPTERS_DIR)
        return all_chapters, saved_files
    
    return [], []


def main():
    parser = argparse.ArgumentParser(
        description='Tự động kiểm tra và scrape chapters mới từ Ko-fi',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--url', '-u', 
                        help='URL của chapter tiếp theo cần scrape')
    parser.add_argument('--target', '-t', type=int,
                        help='Chapter đích (mặc định: hỏi user)')
    parser.add_argument('--count', '-c', type=int,
                        help='Số bài viết cần scrape (thay thế --target)')
    parser.add_argument('--auto', '-a', action='store_true',
                        help='Tự động scrape TẤT CẢ chapters mới đến khi hết')
    parser.add_argument('--delay', '-d', type=int, default=500,
                        help='Delay giữa các request (ms, mặc định: 500)')
    parser.add_argument('--max', '-m', type=int, default=50,
                        help='Giới hạn số bài tối đa khi dùng --auto (mặc định: 50)')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Bỏ qua xác nhận, bắt đầu scrape ngay')
    parser.add_argument('--status', '-s', action='store_true',
                        help='Chỉ hiện trạng thái, không scrape')
    
    args = parser.parse_args()
    
    # Hiển thị banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║             AUTO SCRAPE - Ko-fi Chapter Scraper              ║
╠══════════════════════════════════════════════════════════════╣
║ Tự động kiểm tra và scrape chapters mới                      ║
║                                                              ║
║ Yêu cầu: Chrome chạy với --remote-debugging-port=9222        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Hiển thị trạng thái
    summary = print_status()
    latest_chapter = summary["latest"]
    
    if args.status:
        return
    
    # Chế độ AUTO - scrape tất cả đến khi hết
    if args.auto:
        if not args.url:
            print("\n📎 Nhập URL của chapter tiếp theo cần scrape:")
            print(f"   (Chapter tiếp theo sau Ch.{latest_chapter})")
            args.url = input("   URL: ").strip()
            
            if not args.url:
                print("   ❌ Cần có URL để scrape")
                return
        
        print(f"\n🚀 CHẾ ĐỘ TỰ ĐỘNG - Scrape đến chapter mới nhất!")
        print(f"   • URL: {args.url[:60]}...")
        print(f"   • Delay: {args.delay}ms")
        print(f"   • Giới hạn: {args.max} bài")
        
        if not args.yes:
            confirm = input("\n   Bắt đầu? (y/N): ").strip().lower()
            if confirm != 'y':
                print("   Đã hủy.")
                return
        
        print("\n⏳ Đang scrape tự động...")
        try:
            chapters, output_path = asyncio.run(
                scrape_until_end(args.url, args.delay, args.max)
            )
            
            if chapters:
                print(f"\n✅ HOÀN THÀNH!")
                print(f"   📖 Đã scrape {len(chapters)} chapters")
                print(f"   📁 Đã lưu {len(output_path)} files vào: {CHAPTERS_DIR}")
                print_status()
            else:
                print("\n❌ Không scrape được chapter nào")
                
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()
        
        return
    
    # Chế độ thường - chỉ định count hoặc target
    if args.count:
        count = args.count
        print(f"\n🎯 Sẽ scrape {count} bài viết tiếp theo")
    elif args.target:
        if args.target <= latest_chapter:
            print(f"\n⚠️ Chapter {args.target} đã có rồi!")
            return
        chapters_needed = args.target - latest_chapter
        count = max(1, chapters_needed // 2)
        print(f"\n🎯 Cần scrape khoảng {count} bài để đến Chapter {args.target}")
    else:
        # Hỏi user
        print(f"\n❓ Chapter mới nhất hiện có: {latest_chapter}")
        print("   Tùy chọn:")
        print("   • Nhập số chapter đích (VD: 280)")
        print("   • Nhập 'auto' để scrape tất cả chapters mới")
        print("   • Enter để thoát")
        
        try:
            choice = input("\n   Lựa chọn: ").strip().lower()
            if not choice:
                print("   Đã bỏ qua.")
                return
            
            if choice == 'auto':
                # Chuyển sang chế độ auto
                args.auto = True
                if not args.url:
                    print("\n📎 Nhập URL của chapter tiếp theo:")
                    args.url = input("   URL: ").strip()
                    if not args.url:
                        print("   ❌ Cần có URL")
                        return
                
                print("\n⏳ Đang scrape tự động...")
                chapters, output_path = asyncio.run(
                    scrape_until_end(args.url, args.delay, args.max)
                )
                
                if chapters:
                    print(f"\n✅ HOÀN THÀNH!")
                    print(f"   📖 Đã scrape {len(chapters)} chapters")
                    print(f"   📁 Đã lưu {len(output_path)} files vào: {CHAPTERS_DIR}")
                    print_status()
                return
            
            target = int(choice)
            if target <= latest_chapter:
                print(f"   ⚠️ Chapter {target} đã có rồi!")
                return
            chapters_needed = target - latest_chapter
            count = max(1, chapters_needed // 2)
            print(f"   📝 Sẽ scrape khoảng {count} bài viết")
        except ValueError:
            print("   ❌ Lựa chọn không hợp lệ")
            return
    
    # Yêu cầu URL nếu chưa có
    if not args.url:
        print("\n📎 Nhập URL của chapter tiếp theo cần scrape:")
        print(f"   (Chapter tiếp theo sau Ch.{latest_chapter})")
        args.url = input("   URL: ").strip()
        
        if not args.url:
            print("   ❌ Cần có URL để scrape")
            return
        
        if "ko-fi.com" not in args.url:
            print("   ⚠️ URL không phải Ko-fi, tiếp tục anyway...")
    
    # Xác nhận
    print(f"\n🚀 Sẵn sàng scrape:")
    print(f"   • URL: {args.url[:60]}...")
    print(f"   • Số bài: {count}")
    print(f"   • Delay: {args.delay}ms")
    
    if not args.yes:
        confirm = input("\n   Bắt đầu? (y/N): ").strip().lower()
        if confirm != 'y':
            print("   Đã hủy.")
            return
    
    # Thực hiện scrape
    print("\n⏳ Đang scrape...")
    try:
        chapters, output_path = asyncio.run(
            scrape_new_chapters(args.url, count, args.delay)
        )
        
        if chapters:
            print(f"\n✅ HOÀN THÀNH!")
            print(f"   📖 Đã scrape {len(chapters)} chapters")
            print(f"   📁 Đã lưu {len(output_path)} files vào: {CHAPTERS_DIR}")
            
            # Hiển thị trạng thái mới
            print_status()
        else:
            print("\n❌ Không scrape được chapter nào")
            
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        print("\n💡 Đảm bảo:")
        print("   1. Chrome đang chạy với --remote-debugging-port=9222")
        print("   2. Đã đăng nhập Ko-fi trong Chrome")
        print("   3. URL hợp lệ")


if __name__ == "__main__":
    main()
