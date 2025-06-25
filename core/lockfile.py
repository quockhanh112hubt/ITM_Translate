import ctypes
import os
import tempfile
import tkinter as tk
import sys

# --- LOCK FILE: chỉ cho phép chạy 1 instance ---
LOCK_FILE = os.path.join(tempfile.gettempdir(), "ITMTranslate.lock")

def release_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except Exception:
        pass


def acquire_lock():
    try:
        if os.path.exists(LOCK_FILE):
            # Đọc PID từ file lock
            try:
                with open(LOCK_FILE, "r") as f:
                    old_pid = int(f.read().strip())
            except Exception:
                old_pid = None
            still_running = False
            if old_pid:
                try:
                    if sys.platform.startswith("win"):
                        import ctypes
                        PROCESS_QUERY_INFORMATION = 0x0400
                        process = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, 0, old_pid)
                        if process != 0:
                            exit_code = ctypes.c_ulong()
                            ctypes.windll.kernel32.GetExitCodeProcess(process, ctypes.byref(exit_code))
                            ctypes.windll.kernel32.CloseHandle(process)
                            # 259 = STILL_ACTIVE
                            if exit_code.value == 259:
                                still_running = True
                    else:
                        os.kill(old_pid, 0)
                        still_running = True
                except Exception:
                    still_running = False
            if still_running:
                import tkinter.messagebox as mbox
                root = tk.Tk()
                root.withdraw()
                mbox.showwarning("Warning", "Chương trình đã được khởi động!")
                root.destroy()
                sys.exit()
            else:
                # Nếu process không còn, xóa file lock cũ
                try:
                    os.remove(LOCK_FILE)
                except Exception:
                    pass
        # Ghi file lock mới
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass
