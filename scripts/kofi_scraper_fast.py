"""
Ko-fi Fast Chapter Scraper - Tối ưu hóa tốc độ

So với bản cũ:
- Sử dụng parallel scraping (mở nhiều tab đồng thời)
- Đợi DOM ready thay vì sleep cố định
- Giảm delay giữa các request
- Có thể scrape 5+ chapters trong vài giây

Cách sử dụng:
1. Mở Chrome với debugging:
   chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/ChromeDebug"

2. Login vào Ko-fi trong Chrome

3. Chạy script:
   python kofi_scraper_fast.py --urls "url1" "url2" "url3"
   hoặc
   python kofi_scraper_fast.py --url "start_url" --count 5
   
Tùy chọn:
   --parallel 3    Số tab chạy song song (mặc định: 3)
   --delay 500     Delay giữa các request (ms, mặc định: 500)
"""

import asyncio
import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

try:
    import websockets
    import aiohttp
except ImportError:
    print("Cần cài đặt: pip install websockets aiohttp")
    exit(1)


class FastKofiScraper:
    """Scraper tối ưu với parallel processing"""
    
    def __init__(self, debug_port=9222, parallel_tabs=3, delay_ms=500):
        self.debug_port = debug_port
        self.parallel_tabs = parallel_tabs
        self.delay_ms = delay_ms
        self.sessions: Dict[str, dict] = {}
        self.message_counters: Dict[str, int] = {}
        
    async def get_tabs(self) -> List[dict]:
        """Lấy danh sách tabs từ Chrome"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://localhost:{self.debug_port}/json') as resp:
                return await resp.json()
    
    async def create_new_tab(self, url: str = 'about:blank') -> dict:
        """Tạo tab mới trong Chrome"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'http://localhost:{self.debug_port}/json/new?{url}'
            ) as resp:
                return await resp.json()
    
    async def close_tab(self, tab_id: str):
        """Đóng tab"""
        async with aiohttp.ClientSession() as session:
            await session.get(f'http://localhost:{self.debug_port}/json/close/{tab_id}')
    
    async def connect_to_tab(self, tab: dict) -> websockets.WebSocketClientProtocol:
        """Kết nối WebSocket đến tab"""
        ws_url = tab['webSocketDebuggerUrl']
        ws = await websockets.connect(ws_url)
        tab_id = tab['id']
        self.sessions[tab_id] = {'ws': ws, 'tab': tab}
        self.message_counters[tab_id] = 0
        return ws
    
    async def send_command(self, tab_id: str, method: str, params: dict = None) -> dict:
        """Gửi CDP command"""
        self.message_counters[tab_id] += 1
        msg_id = self.message_counters[tab_id]
        
        ws = self.sessions[tab_id]['ws']
        message = {'id': msg_id, 'method': method, 'params': params or {}}
        
        await ws.send(json.dumps(message))
        
        while True:
            response = await ws.recv()
            data = json.loads(response)
            if data.get('id') == msg_id:
                if 'error' in data:
                    raise Exception(f"CDP Error: {data['error']}")
                return data.get('result', {})
    
    async def wait_for_page_load(self, tab_id: str, timeout: float = 10.0):
        """Đợi page load xong - tối ưu hơn sleep cố định"""
        ws = self.sessions[tab_id]['ws']
        
        # Enable Page domain events
        await self.send_command(tab_id, 'Page.enable')
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Timeout ngắn để check events
                response = await asyncio.wait_for(ws.recv(), timeout=0.5)
                data = json.loads(response)
                
                # Tìm loadEventFired event
                if data.get('method') == 'Page.loadEventFired':
                    # Page đã load xong, đợi thêm chút cho Shadow DOM
                    await asyncio.sleep(0.3)
                    return True
                    
            except asyncio.TimeoutError:
                pass
            
            # Check timeout tổng
            if asyncio.get_event_loop().time() - start_time > timeout:
                # Timeout, nhưng vẫn tiếp tục thử extract
                return False
    
    async def navigate_and_wait(self, tab_id: str, url: str) -> bool:
        """Navigate đến URL và đợi load xong"""
        await self.send_command(tab_id, 'Page.navigate', {'url': url})
        return await self.wait_for_page_load(tab_id)
    
    async def execute_js(self, tab_id: str, expression: str):
        """Thực thi JavaScript"""
        result = await self.send_command(tab_id, 'Runtime.evaluate', {
            'expression': expression,
            'returnByValue': True,
            'awaitPromise': True
        })
        
        if 'exceptionDetails' in result:
            raise Exception(f"JS Error: {result['exceptionDetails']}")
        
        return result.get('result', {}).get('value')
    
    async def extract_chapter_from_tab(self, tab_id: str) -> dict:
        """Extract content từ một tab"""
        js_code = '''
        (() => {
            const titleElement = document.querySelector('h1') || document.querySelector('h2');
            const postTitle = titleElement ? titleElement.innerText.trim() : document.title;
            
            const articleHost = document.querySelector('.article-host');
            let bodyText = '';
            let nextUrl = null;
            
            if (articleHost && articleHost.shadowRoot) {
                const shadowRoot = articleHost.shadowRoot;
                const frView = shadowRoot.querySelector('.fr-view');
                
                bodyText = frView ? frView.innerText : (shadowRoot.textContent || '');
                
                const shadowLinks = Array.from(shadowRoot.querySelectorAll('a'));
                for (const link of shadowLinks) {
                    const text = link.innerText.toLowerCase();
                    if (text.includes('next chapter') || text.includes('>> next')) {
                        nextUrl = link.href;
                        break;
                    }
                }
            } else {
                bodyText = document.body.innerText;
            }
            
            if (!nextUrl) {
                const links = Array.from(document.querySelectorAll('a'));
                for (const link of links) {
                    const text = link.innerText.toLowerCase();
                    if (text.includes('next chapter') || text.includes('>> next')) {
                        nextUrl = link.href;
                        break;
                    }
                }
            }
            
            return JSON.stringify({
                title: postTitle,
                url: window.location.href,
                content: bodyText,
                nextChapterUrl: nextUrl
            });
        })()
        '''
        
        result = await self.execute_js(tab_id, js_code)
        return json.loads(result)
    
    async def scrape_single_url(self, url: str, tab: dict = None) -> Tuple[List[dict], str]:
        """Scrape một URL, trả về chapters và next URL"""
        close_tab = False
        
        if tab is None:
            # Tạo tab mới
            tab = await self.create_new_tab()
            close_tab = True
        
        tab_id = tab['id']
        
        try:
            await self.connect_to_tab(tab)
            await self.navigate_and_wait(tab_id, url)
            
            data = await self.extract_chapter_from_tab(tab_id)
            chapters = parse_chapters_from_content(data['content'], data['title'])
            
            return chapters, data.get('nextChapterUrl')
            
        finally:
            # Cleanup
            if tab_id in self.sessions:
                await self.sessions[tab_id]['ws'].close()
                del self.sessions[tab_id]
            
            if close_tab:
                await self.close_tab(tab_id)
    
    async def scrape_urls_parallel(self, urls: List[str]) -> List[dict]:
        """Scrape nhiều URLs song song"""
        all_chapters = []
        
        # Chia thành batches
        for i in range(0, len(urls), self.parallel_tabs):
            batch = urls[i:i + self.parallel_tabs]
            
            print(f"\n🚀 Scraping batch {i // self.parallel_tabs + 1} ({len(batch)} URLs song song)...")
            
            # Scrape song song trong batch
            tasks = [self.scrape_single_url(url) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for j, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"   ❌ Lỗi với URL {batch[j]}: {result}")
                else:
                    chapters, _ = result
                    all_chapters.extend(chapters)
                    print(f"   ✅ Góp {len(chapters)} chapter(s)")
            
            # Delay giữa các batch
            if i + self.parallel_tabs < len(urls):
                await asyncio.sleep(self.delay_ms / 1000)
        
        return all_chapters
    
    async def scrape_sequential_with_next(self, start_url: str, count: int) -> List[dict]:
        """Scrape tuần tự theo link Next Chapter - nhưng tối ưu hơn"""
        all_chapters = []
        current_url = start_url
        
        # Lấy tab hiện có hoặc tạo mới
        tabs = await self.get_tabs()
        kofi_tab = None
        for tab in tabs:
            if tab.get('type') == 'page' and 'ko-fi' in tab.get('url', ''):
                kofi_tab = tab
                break
        
        if not kofi_tab:
            kofi_tab = tabs[0] if tabs else await self.create_new_tab()
        
        tab_id = kofi_tab['id']
        
        try:
            await self.connect_to_tab(kofi_tab)
            
            for i in range(count):
                print(f"\n📖 [{i + 1}/{count}] Scraping: {current_url[:60]}...")
                
                # Navigate và đợi
                loaded = await self.navigate_and_wait(tab_id, current_url)
                if not loaded:
                    print("   ⚠️ Page load timeout, thử extract anyway...")
                
                # Extract
                data = await self.extract_chapter_from_tab(tab_id)
                chapters = parse_chapters_from_content(data['content'], data['title'])
                
                all_chapters.extend(chapters)
                
                for ch in chapters:
                    print(f"   ✅ Chapter {ch['id']}: {ch['title'][:40]}...")
                
                # Next URL
                if data.get('nextChapterUrl') and i < count - 1:
                    current_url = data['nextChapterUrl']
                    # Delay ngắn
                    await asyncio.sleep(self.delay_ms / 1000)
                else:
                    if i < count - 1:
                        print("   ⚠️ Không tìm thấy link Next Chapter")
                    break
                    
        finally:
            if tab_id in self.sessions:
                await self.sessions[tab_id]['ws'].close()
        
        return all_chapters


def clean_text(text: str) -> str:
    """Làm sạch text"""
    lines = text.split('\n')
    
    skip_patterns = [
        r'^>> Next Chapter',
        r'^<< Previous Chapter',
        r'^Support me',
        r'^Buy me a coffee',
        r'^Ko-fi',
        r'^See all$',
        r'^Terms$',
        r'^Privacy$',
        r'^\d+ comments?$',
        r'^Share$',
        r'^Like$',
        r'^Your page$',
        r'^T$',
        r'^\d+ \w+ \d+$',
        r'^Explore$',
        r'^Notifications$',
        r'^\d{1,2}$',
    ]
    
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue
        
        skip = False
        for pattern in skip_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                skip = True
                break
        
        if not skip:
            cleaned.append(line)
    
    return '\n\n'.join(cleaned)


def parse_chapters_from_content(content: str, title: str) -> List[dict]:
    """Parse chapters từ content"""
    vol_match = re.search(r'Vol\.?\s*(\d+)', title, re.IGNORECASE)
    volume = int(vol_match.group(1)) if vol_match else 1
    
    pattern = r'\[Vol\.\s*\d+\]\s*Chapter\s*(\d+):\s*([^\n]+)'
    matches = list(re.finditer(pattern, content, re.IGNORECASE))
    
    chapters = []
    
    if matches:
        for i, match in enumerate(matches):
            chapter_num = int(match.group(1))
            chapter_title = match.group(2).strip()
            
            start_idx = match.end()
            end_idx = matches[i + 1].start() if i < len(matches) - 1 else len(content)
            chapter_content = clean_text(content[start_idx:end_idx])
            
            chapters.append({
                'id': chapter_num,
                'volume': volume,
                'title': chapter_title,
                'content': chapter_content
            })
    else:
        ch_match = re.search(r'Chapter\s*(\d+)', title, re.IGNORECASE)
        chapter_num = int(ch_match.group(1)) if ch_match else 1
        
        chapters.append({
            'id': chapter_num,
            'volume': volume,
            'title': title,
            'content': clean_text(content)
        })
    
    return chapters


def format_to_xml(chapters: List[dict]) -> str:
    """Format chapters thành XML"""
    def escape_xml(text):
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<chapters>\n'
    
    for ch in chapters:
        xml += f'  <chapter number="{ch["id"]}" volume="{ch["volume"]}">\n'
        xml += f'    <title>{escape_xml(ch["title"])}</title>\n'
        xml += f'    <text>{escape_xml(ch["content"])}</text>\n'
        xml += f'  </chapter>\n'
    
    xml += '</chapters>'
    return xml


def save_chapters(chapters: List[dict], output_dir: Path = None) -> Path:
    """Lưu chapters ra file"""
    if not chapters:
        return None
    
    chapter_ids = [ch['id'] for ch in chapters]
    min_ch, max_ch = min(chapter_ids), max(chapter_ids)
    
    filename = f"ch{min_ch}_{max_ch}.txt" if min_ch != max_ch else f"ch{min_ch}.txt"
    
    if output_dir:
        output_path = Path(output_dir) / filename
    else:
        output_path = Path(__file__).parent / 'Chapters_Untranslated' / filename
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    xml_content = format_to_xml(chapters)
    output_path.write_text(xml_content, encoding='utf-8')
    
    return output_path


async def main_async(args):
    """Main async function"""
    scraper = FastKofiScraper(
        debug_port=args.port,
        parallel_tabs=args.parallel,
        delay_ms=args.delay
    )
    
    if args.urls:
        # Scrape nhiều URLs song song
        print(f"🚀 Parallel scraping {len(args.urls)} URLs (max {args.parallel} đồng thời)...")
        chapters = await scraper.scrape_urls_parallel(args.urls)
    else:
        # Scrape tuần tự theo Next Chapter
        print(f"🚀 Sequential scraping từ {args.url}, {args.count} bài viết...")
        chapters = await scraper.scrape_sequential_with_next(args.url, args.count)
    
    if chapters:
        output_path = save_chapters(chapters, args.output)
        print(f"\n✅ Hoàn thành! Đã lưu {len(chapters)} chapters vào: {output_path}")
    else:
        print("\n❌ Không extract được chapter nào.")
    
    return chapters


def main():
    parser = argparse.ArgumentParser(
        description='Ko-fi Fast Scraper - Tối ưu tốc độ với parallel processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ví dụ sử dụng:
  # Scrape 5 bài từ một URL theo link Next Chapter
  python kofi_scraper_fast.py --url "https://ko-fi.com/post/..." --count 5
  
  # Scrape nhiều URLs song song
  python kofi_scraper_fast.py --urls "url1" "url2" "url3" --parallel 3
  
  # Điều chỉnh delay (mặc định 500ms)
  python kofi_scraper_fast.py --url "..." --count 10 --delay 300
        '''
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', '-u', help='URL bắt đầu (dùng với --count)')
    group.add_argument('--urls', nargs='+', help='Danh sách URLs để scrape song song')
    
    parser.add_argument('--count', '-c', type=int, default=1,
                        help='Số bài viết cần scrape khi dùng --url (mặc định: 1)')
    parser.add_argument('--output', '-o', help='Thư mục output')
    parser.add_argument('--port', '-p', type=int, default=9222,
                        help='Chrome debugging port (mặc định: 9222)')
    parser.add_argument('--parallel', type=int, default=3,
                        help='Số tabs chạy song song (mặc định: 3)')
    parser.add_argument('--delay', type=int, default=500,
                        help='Delay giữa các batch (ms, mặc định: 500)')
    
    args = parser.parse_args()
    
    print("""
╔════════════════════════════════════════════════════════════╗
║         Ko-fi FAST Chapter Scraper (Optimized)             ║
╠════════════════════════════════════════════════════════════╣
║ Đảm bảo Chrome đang chạy với debugging:                    ║
║   chrome.exe --remote-debugging-port=9222                  ║
║                                                            ║
║ Tối ưu: Parallel scraping, Smart wait, Reduced delays     ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main_async(args))


if __name__ == '__main__':
    main()
