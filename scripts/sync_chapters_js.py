#!/usr/bin/env python3
"""
Script to sync chapters.json to chapters.js

This script reads website/data/chapters.json and updates website/js/chapters.js
to match, wrapping the JSON data in a JavaScript variable declaration.
"""

import json
import os
from pathlib import Path


def get_project_root():
    """Get project root directory"""
    script_dir = Path(__file__).parent
    return script_dir.parent


def sync_chapters_js():
    """Sync chapters.json to chapters.js"""
    project_root = get_project_root()
    
    # Paths
    json_path = project_root / "website" / "data" / "chapters.json"
    js_path = project_root / "website" / "js" / "chapters.js"
    
    print(f"🔄 Syncing chapters.json to chapters.js...")
    print(f"   Source: {json_path}")
    print(f"   Target: {js_path}")
    
    # Read chapters.json
    if not json_path.exists():
        print(f"❌ Error: chapters.json not found at {json_path}")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            chapters_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse chapters.json - {e}")
        return False
    except Exception as e:
        print(f"❌ Error: Failed to read chapters.json - {e}")
        return False
    
    # Update totalChapters count
    if "chapters" in chapters_data:
        chapters_data["totalChapters"] = len(chapters_data["chapters"])
        print(f"   📊 Total chapters: {chapters_data['totalChapters']}")
    
    # Format JSON with proper indentation
    json_content = json.dumps(chapters_data, ensure_ascii=False, indent=2)
    
    # Create JavaScript content
    js_content = f"""// Auto-generated chapter data
const chaptersData = {json_content};
"""
    
    # Ensure directory exists
    js_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to chapters.js
    try:
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
    except Exception as e:
        print(f"❌ Error: Failed to write chapters.js - {e}")
        return False
    
    print(f"✅ Successfully synced chapters.js!")
    print(f"   📝 File size: {len(js_content):,} bytes")
    
    return True


def main():
    """Main entry point"""
    print("=" * 50)
    print("📦 Sync Chapters.json to Chapters.js")
    print("=" * 50)
    
    success = sync_chapters_js()
    
    if success:
        print("\n✅ Sync completed successfully!")
        return 0
    else:
        print("\n❌ Sync failed!")
        return 1


if __name__ == "__main__":
    exit(main())
