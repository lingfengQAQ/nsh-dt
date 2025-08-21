import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageGrab
import threading
import time

class ScreenshotTool:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.overlay_window = None
        self.is_active = False
        self.selection_rect = None
        
        # 默认截图区域位置和大小
        self.default_x = 100
        self.default_y = 100
        self.default_width = 400
        self.default_height = 300
        
    def show_overlay(self):
        """显示截图区域选择框"""
        if self.overlay_window is not None:
            return
            
        self.is_active = True
        self.create_overlay_window()
        
    def hide_overlay(self):
        """隐藏截图区域选择框"""
        if self.overlay_window is not None:
            self.overlay_window.destroy()
            self.overlay_window = None
        self.is_active = False
        
    def create_overlay_window(self):
        """创建悬浮的截图区域选择框"""
        self.overlay_window = tk.Toplevel()
        self.overlay_window.title("截图区域")
        self.overlay_window.geometry(f"{self.default_width}x{self.default_height}+{self.default_x}+{self.default_y}")
        
        # 设置窗口属性
        self.overlay_window.attributes('-topmost', True)  # 置顶
        self.overlay_window.attributes('-alpha', 0.8)     # 半透明
        self.overlay_window.attributes('-transparentcolor', 'white')  # 设置透明色
        self.overlay_window.resizable(True, True)         # 可调整大小
        
        # 设置窗口样式
        self.overlay_window.configure(bg='green')
        
        # 创建主框架
        main_frame = tk.Frame(self.overlay_window, bg='green', bd=2, relief='solid')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 创建内部透明区域（使用白色作为透明色）
        inner_frame = tk.Frame(main_frame, bg='white', bd=0)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 绑定快捷键：Enter 键进行截图，Esc 键隐藏窗口
        self.overlay_window.bind('<Return>', lambda e: self.capture_current_area())
        self.overlay_window.bind('<Escape>', lambda e: self.hide_overlay())
        
        # 绑定窗口关闭事件
        self.overlay_window.protocol("WM_DELETE_WINDOW", self.hide_overlay)
        
        # 绑定拖拽事件（用于移动窗口）
        self.bind_drag_events()
        
    def bind_drag_events(self):
        """绑定拖拽事件"""
        self.overlay_window.bind('<Button-1>', self.start_drag)
        self.overlay_window.bind('<B1-Motion>', self.on_drag)
        
    def start_drag(self, event):
        """开始拖拽"""
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.drag_start_window_x = self.overlay_window.winfo_x()
        self.drag_start_window_y = self.overlay_window.winfo_y()
        
    def on_drag(self, event):
        """拖拽过程中"""
        if hasattr(self, 'drag_start_x'):
            dx = event.x_root - self.drag_start_x
            dy = event.y_root - self.drag_start_y
            new_x = self.drag_start_window_x + dx
            new_y = self.drag_start_window_y + dy
            self.overlay_window.geometry(f"+{new_x}+{new_y}")
            
    def capture_current_area(self):
        """截图当前选择区域"""
        if self.overlay_window is None:
            return None
            
        # 获取窗口位置和大小
        x = self.overlay_window.winfo_x()
        y = self.overlay_window.winfo_y()
        width = self.overlay_window.winfo_width()
        height = self.overlay_window.winfo_height()
        
        # 暂时隐藏窗口以避免截图包含窗口本身
        self.overlay_window.withdraw()
        
        # 等待窗口完全隐藏
        time.sleep(0.1)
        
        try:
            # 截图指定区域
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            
            # 恢复窗口显示
            self.overlay_window.deiconify()
            
            return screenshot
            
        except Exception as e:
            # 恢复窗口显示
            self.overlay_window.deiconify()
            raise e
            
    def capture_area(self):
        """截图选定区域（主要接口）"""
        return self.capture_current_area()
        
    def cleanup(self):
        """清理资源"""
        if self.overlay_window is not None:
            try:
                self.overlay_window.destroy()
            except:
                pass
            self.overlay_window = None
        self.is_active = False
