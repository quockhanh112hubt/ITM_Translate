#!/usr/bin/env python3
"""
Script để tạo GitHub release và upload file
"""
import os
import json
import subprocess
import sys

def create_github_release():
    """Tạo GitHub release"""
    
    # Đọc thông tin version
    with open('version.json', 'r') as f:
        version_data = json.load(f)
    
    version = version_data['version']
    build = version_data['build']
    description = version_data['description']
    release_date = version_data['release_date']
    
    # Đọc changelog
    changelog_file = f"CHANGELOG_v{version}.md"
    if os.path.exists(changelog_file):
        with open(changelog_file, 'r', encoding='utf-8') as f:
            changelog = f.read()
    else:
        changelog = f"Release notes for ITM Translate v{version}"
    
    print(f"=== Tạo GitHub Release v{version} ===")
    print(f"Version: {version}")
    print(f"Build: {build}")
    print(f"Date: {release_date}")
    print(f"Description: {description}")
    print()
    
    # Tạo release body
    release_body = f"""# ITM Translate v{version}

## 📅 Release Date: {release_date}
## 🔧 Build: {build}

{description}

---

## 📋 Changelog
{changelog}

---

## 📥 Download
- **ITM_Translate.exe**: Main executable file
- **Source code**: Available in ZIP and TAR formats

## 🔧 Installation
1. Download `ITM_Translate.exe`
2. Run the executable
3. For updates: Use the built-in update feature

## 📝 Notes
- This version includes auto-update functionality
- Backup your settings before updating
- Report issues at GitHub Issues
"""
    
    # Kiểm tra file exe tồn tại
    exe_file = "dist/ITM_Translate.exe"
    if not os.path.exists(exe_file):
        print(f"❌ File không tồn tại: {exe_file}")
        return False
    
    # Hiển thị thông tin file
    file_size = os.path.getsize(exe_file)
    print(f"📁 File: {exe_file}")
    print(f"📊 Size: {file_size/1024/1024:.2f} MB")
    print()
    
    # Tạo release notes file
    release_notes_file = f"release_notes_v{version}.md"
    with open(release_notes_file, 'w', encoding='utf-8') as f:
        f.write(release_body)
    
    print(f"✅ Release notes saved to: {release_notes_file}")
    print()
    print("🚀 Để tạo release trên GitHub:")
    print("1. Truy cập: https://github.com/yourusername/ITM_Translate/releases")
    print("2. Nhấn 'Create a new release'")
    print(f"3. Tag: v{version}")
    print(f"4. Title: ITM Translate v{version}")
    print(f"5. Copy nội dung từ file: {release_notes_file}")
    print(f"6. Upload file: {exe_file}")
    print("7. Nhấn 'Publish release'")
    print()
    
    return True

if __name__ == "__main__":
    create_github_release()
