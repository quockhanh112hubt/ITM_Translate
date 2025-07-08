#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime

def run_command(cmd, check=True):
    """Chạy command và return kết quả"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def main():
    print("=" * 50)
    print("  ITM Translate - Auto Build & Release")
    print("=" * 50)
    
    # Kiểm tra Git repository
    if not os.path.exists('.git'):
        print("ERROR: Đây không phải là Git repository!")
        sys.exit(1)
    
    # Kiểm tra thay đổi chưa commit
    success, output, _ = run_command("git status --porcelain")
    if success and output.strip():
        print("WARNING: Có thay đổi chưa được commit!")
        continue_build = input("Bạn có muốn tiếp tục? (y/N): ")
        if continue_build.lower() != 'y':
            print("Đã hủy.")
            sys.exit(1)
    
    # Đọc version hiện tại
    current_version = "1.0.0"
    try:
        with open('version.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            current_version = data.get('version', '1.0.0')
    except Exception:
        pass
    
    print(f"Version hiện tại: {current_version}")
    
    # Nhập version mới
    new_version = input(f"Nhập version mới (Enter để giữ {current_version}): ").strip()
    if not new_version:
        new_version = current_version
    
    # Tạo build number
    build_num = datetime.now().strftime("%Y%m%d%H")
    
    print(f"\nVersion: {new_version}")
    print(f"Build: {build_num}")
    
    # Cập nhật version.json
    print("\nCập nhật version.json...")
    version_data = {
        "version": new_version,
        "build": build_num,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "description": "Auto build release"
    }
    
    with open('version.json', 'w', encoding='utf-8') as f:
        json.dump(version_data, f, indent=4, ensure_ascii=False)
    
    # Build với PyInstaller
    print("\n" + "=" * 50)
    print("  Bắt đầu build executable...")
    print("=" * 50)
    
    # Xóa thư mục cũ
    if os.path.exists('dist'):
        import shutil
        shutil.rmtree('dist')
    if os.path.exists('build'):
        import shutil
        shutil.rmtree('build')
    
    # Build command - có thể dùng spec file hoặc command line
    use_spec_file = os.path.exists("ITM_Translate.spec")
    
    if use_spec_file:
        build_cmd_str = "python -m PyInstaller ITM_Translate.spec"
        print("Sử dụng spec file để build...")
    else:
        build_cmd_str = 'python -m PyInstaller --onefile --windowed --hidden-import=ttkbootstrap --icon="Resource/icon.ico" --add-data "Resource/icon.ico;Resource" --name="ITM_Translate" ITM_Translate.py'
        print("Sử dụng command line để build...")
    
    print(f"Running: {build_cmd_str}")
    success, output, error = run_command(build_cmd_str)
    
    if not success:
        print(f"ERROR: Build thất bại!")
        print(f"Output: {output}")
        print(f"Error: {error}")
        sys.exit(1)
    
    # Kiểm tra file output
    exe_name = "ITM_Translate.exe" if sys.platform == "win32" else "ITM_Translate"
    exe_path = os.path.join("dist", exe_name)
    
    if not os.path.exists(exe_path):
        print(f"ERROR: Không tìm thấy file build: {exe_path}")
        sys.exit(1)
    
    print(f"Build thành công: {exe_path}")
    
    # Git commit và tag
    print("\n" + "=" * 50)
    print("  Git commit và tạo tag...")
    print("=" * 50)
    
    run_command("git add .")
    run_command(f'git commit -m "Release v{new_version} - Build {build_num}"')
    run_command(f'git tag -a "v{new_version}" -m "Release version {new_version}"')
    
    print(f"Đã tạo tag: v{new_version}")
    
    # Hỏi có muốn push không
    push_confirm = input("\nBạn có muốn push lên GitHub không? (y/N): ")
    if push_confirm.lower() == 'y':
        print("Đang push...")
        success1, _, _ = run_command("git push origin main", check=False)
        success2, _, _ = run_command("git push origin --tags", check=False)
        
        if success1 and success2:
            print("Push thành công!")
        else:
            print("Push có lỗi, vui lòng kiểm tra lại.")
    else:
        print("Đã skip push. Bạn có thể push sau bằng:")
        print("  git push origin main")
        print("  git push origin --tags")
    
    print("\n" + "=" * 50)
    print("  Hoàn thành!")
    print("=" * 50)
    print(f"File build: {exe_path}")
    print(f"Version: {new_version}")
    print(f"Build: {build_num}")
    print(f"Tag: v{new_version}")
    print("\nTiếp theo:")
    print(f"1. Tạo release trên GitHub từ tag v{new_version}")
    print(f"2. Upload file {exe_path} vào release")
    print("3. Viết changelog cho release")

if __name__ == "__main__":
    main()
