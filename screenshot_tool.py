import tkinter as tk
from PIL import ImageGrab
import time

class ScreenshotTool:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.overlay_window = None
        self.is_active = False
        # Default geometry for the first launch
        self.last_x = 100
        self.last_y = 100
        self.last_width = 400
        self.last_height = 300

    def show_overlay(self):
        self.is_active = True
        if self.overlay_window is None:
            self.create_overlay_window()
        else:
            self.overlay_window.deiconify()

    def hide_overlay(self):
        if self.overlay_window is not None:
            self.overlay_window.withdraw()
        self.is_active = False

    def create_overlay_window(self):
        self.overlay_window = tk.Toplevel()
        self.overlay_window.overrideredirect(True)
        self.overlay_window.geometry(f"{self.last_width}x{self.last_height}+{self.last_x}+{self.last_y}")
        self.overlay_window.attributes('-topmost', True)
        self.overlay_window.attributes('-alpha', 0.8)
        
        self.canvas = tk.Canvas(self.overlay_window, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.overlay_window.configure(bg='white')
        self.overlay_window.attributes('-transparentcolor', 'white')

        self.draw_overlay()

        self.overlay_window.bind('<Escape>', lambda e: self.parent_app.toggle_screenshot_area())
        self.overlay_window.bind('<Return>', lambda e: self.parent_app.capture_and_recognize())
        self.overlay_window.bind('<Configure>', self.on_resize_or_move)

        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        
        self.create_resize_handles()

    def draw_overlay(self):
        self.canvas.delete("all")
        width = self.overlay_window.winfo_width()
        height = self.overlay_window.winfo_height()
        
        self.canvas.create_rectangle(0, 0, width, height, fill="gray50", outline="")
        self.canvas.create_rectangle(0, 0, width-1, height-1, outline="blue", width=2)

    def on_resize_or_move(self, event):
        # Persist the last known geometry
        if self.overlay_window.winfo_width() > 20 and self.overlay_window.winfo_height() > 20:
            self.last_width = self.overlay_window.winfo_width()
            self.last_height = self.overlay_window.winfo_height()
            self.last_x = self.overlay_window.winfo_x()
            self.last_y = self.overlay_window.winfo_y()
        self.draw_overlay()

    def start_drag(self, event):
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def on_drag(self, event):
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y
        x = self.overlay_window.winfo_x() + dx
        y = self.overlay_window.winfo_y() + dy
        self.overlay_window.geometry(f"+{x}+{y}")
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def create_resize_handles(self):
        handle_size = 10
        
        tl_handle = tk.Frame(self.overlay_window, bg='blue', cursor='size_nw_se')
        tl_handle.place(x=0, y=0, width=handle_size, height=handle_size)
        self.bind_resize(tl_handle, "tl")

        tr_handle = tk.Frame(self.overlay_window, bg='blue', cursor='size_ne_sw')
        tr_handle.place(relx=1.0, y=0, anchor='ne', width=handle_size, height=handle_size)
        self.bind_resize(tr_handle, "tr")

        bl_handle = tk.Frame(self.overlay_window, bg='blue', cursor='size_ne_sw')
        bl_handle.place(x=0, rely=1.0, anchor='sw', width=handle_size, height=handle_size)
        self.bind_resize(bl_handle, "bl")

        br_handle = tk.Frame(self.overlay_window, bg='blue', cursor='size_nw_se')
        br_handle.place(relx=1.0, rely=1.0, anchor='se', width=handle_size, height=handle_size)
        self.bind_resize(br_handle, "br")

    def bind_resize(self, widget, corner):
        widget.bind("<Button-1>", lambda e, c=corner: self.start_resize(e, c))
        widget.bind("<B1-Motion>", self.on_resize)

    def start_resize(self, event, corner):
        self.resize_corner = corner
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.resize_start_width = self.overlay_window.winfo_width()
        self.resize_start_height = self.overlay_window.winfo_height()
        self.resize_start_win_x = self.overlay_window.winfo_x()
        self.resize_start_win_y = self.overlay_window.winfo_y()

    def on_resize(self, event):
        if not hasattr(self, 'resize_corner'):
            return

        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y

        x, y = self.resize_start_win_x, self.resize_start_win_y
        width, height = self.resize_start_width, self.resize_start_height

        if "r" in self.resize_corner:
            width += dx
        if "l" in self.resize_corner:
            width -= dx
            x += dx
        if "b" in self.resize_corner:
            height += dy
        if "t" in self.resize_corner:
            height -= dy
            y += dy

        if width > 20 and height > 20:
            self.overlay_window.geometry(f"{width}x{height}+{x}+{y}")

    def capture_area(self):
        if self.overlay_window is None or not self.is_active:
            return None
        
        x = self.overlay_window.winfo_x()
        y = self.overlay_window.winfo_y()
        width = self.overlay_window.winfo_width()
        height = self.overlay_window.winfo_height()
        
        # Hide the window to capture what's underneath
        self.overlay_window.withdraw()
        time.sleep(0.1) # Give time for the window to disappear
        
        try:
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            # NOTE: We do NOT deiconify here anymore. The main app will decide when to show it again.
            return screenshot
        except Exception as e:
            # Ensure the window is shown again if capture fails
            self.overlay_window.deiconify()
            raise e

    def cleanup(self):
        if self.overlay_window is not None:
            self.overlay_window.destroy()
            self.overlay_window = None