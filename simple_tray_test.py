import tkinter as tk
import win32api
import win32con
import win32gui
import sys
from PIL import Image

class SysTrayApp:
    def __init__(self, root):
        self.root = root
        self.hwnd = None
        self.icon_a = "icon_ON.ico"
        self.icon_b = "icon_OFF.ico"
        self.current_icon = self.icon_a
        self.tray_active = False

        self.root.title("Demo Tray")
        self.root.geometry("300x150")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.message_map = {
            win32con.WM_DESTROY: self.on_destroy,
            win32con.WM_COMMAND: self.on_command,
            win32con.WM_USER+20: self.on_tray_notify,
        }

        self._register_window()

    def _register_window(self):
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "MyTrayApp"
        wc.lpfnWndProc = self.message_map
        classAtom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(
            wc.lpszClassName, "Hidden Tray Window",
            0, 0, 0, 0, 0, 0, 0, hinst, None
        )

    def hide_window(self):
        self.root.withdraw()
        if not self.tray_active:
            self._create_tray_icon()
            self.tray_active = True

    def show_window(self):
        self.root.deiconify()

    def _create_tray_icon(self):
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = win32gui.LoadImage(
            0, self.current_icon, win32con.IMAGE_ICON, 0, 0, icon_flags
        )
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "Ứng dụng của bạn")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

    def _update_tray_icon(self, icon_path):
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = win32gui.LoadImage(
            0, icon_path, win32con.IMAGE_ICON, 0, 0, icon_flags
        )
        # Đảm bảo tooltip không phải None
        nid = (self.hwnd, 0,
            win32gui.NIF_ICON | win32gui.NIF_TIP,
            win32con.WM_USER+20, hicon,
            "Ứng dụng của bạn")  # Đây là tooltip hợp lệ
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)


    def on_destroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)

    def on_command(self, hwnd, msg, wparam, lparam):
        id = win32api.LOWORD(wparam)
        if id == 1023:
            self.show_window()
        elif id == 1024:
            win32gui.DestroyWindow(self.hwnd)

    def on_tray_notify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONUP:
            # Click chuột trái → đổi icon
            if self.current_icon == self.icon_a:
                self.current_icon = self.icon_b
            else:
                self.current_icon = self.icon_a
            self._update_tray_icon(self.current_icon)
        elif lparam == win32con.WM_RBUTTONUP:
            # Chuột phải → hiện menu
            menu = win32gui.CreatePopupMenu()
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1023, "Hiện lại cửa sổ")
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1024, "Thoát")
            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN,
                                    pos[0], pos[1], 0, self.hwnd, None)
        return True

    def run(self):
        win32gui.PumpMessages()


if __name__ == '__main__':
    root = tk.Tk()
    app = SysTrayApp(root)
    tk_thread = root.mainloop()

    # Đảm bảo thoát khỏi loop nếu cần
    sys.exit()
