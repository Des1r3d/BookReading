"""
Parse Vietnamese chapter files and generate chapters.json for the website.
Handles multi-chapter XML files from the Chapters directory.
"""

import os
import re
import json
from pathlib import Path

def parse_chapter_file(filepath):
    """Parse a single chapter file and extract individual chapters."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chapters = []
    
    # Find all chapter blocks
    chapter_pattern = r'<chapter number="(\d+)" volume="(\d+)">\s*<title>(.*?)</title>\s*<text>(.*?)</text>\s*</chapter>'
    matches = re.findall(chapter_pattern, content, re.DOTALL)
    
    for match in matches:
        chapter_num = int(match[0])
        volume = int(match[1])
        title = match[2].strip()
        text = match[3].strip()
        
        # Clean up the text - remove extra whitespace but keep paragraph structure
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        clean_text = '\n\n'.join(paragraphs)
        
        chapters.append({
            'id': chapter_num,
            'volume': volume,
            'title': title,
            'content': clean_text
        })
    
    return chapters

def main():
    # Paths
    script_dir = Path(__file__).parent
    chapters_dir = script_dir.parent / 'Chapters'
    output_dir = script_dir.parent / 'website' / 'data'
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_chapters = []
    
    # Process all .vn.txt files
    chapter_files = sorted(chapters_dir.glob('*.vn.txt'))
    
    print(f"Found {len(chapter_files)} chapter files")
    
    for filepath in chapter_files:
        print(f"Processing: {filepath.name}")
        try:
            chapters = parse_chapter_file(filepath)
            all_chapters.extend(chapters)
            print(f"  - Extracted {len(chapters)} chapters")
        except Exception as e:
            print(f"  - Error: {e}")
    
    # Sort chapters by ID
    all_chapters.sort(key=lambda x: x['id'])
    
    # Create the output data structure
    output_data = {
        'bookTitle': 'Max Level Priest',
        'bookTitleVi': 'Linh Mục Cấp Tối Đa',
        'totalChapters': len(all_chapters),
        'chapters': all_chapters
    }
    
    # Write JSON file
    output_path = output_dir / 'chapters.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nGenerated {output_path}")
    print(f"Total chapters: {len(all_chapters)}")
    if all_chapters:
        print(f"Chapter range: {all_chapters[0]['id']} - {all_chapters[-1]['id']}")
    
    # Also generate a JS file for direct inclusion (no fetch needed)
    js_output_path = script_dir.parent / 'website' / 'js' / 'chapters.js'
    with open(js_output_path, 'w', encoding='utf-8') as f:
        f.write('// Auto-generated chapter data\n')
        f.write('const chaptersData = ')
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        f.write(';\n')
    
    print(f"Generated {js_output_path}")

if __name__ == '__main__':
    main()
