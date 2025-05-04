from ttkbootstrap import Style, ttk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk

class MenuFrame(ttk.Frame):
    def __init__(self, parent, width=120, callbacks=None):
        super().__init__(parent)
        self.parent = parent
        self.callbacks = callbacks or {}
        
        # Configure frame style
        self.style = Style()
        self.style.configure('Custom.TFrame')
        
        # Configure the frame
        self.configure(style='Custom.TFrame', width=width)
        self.pack(fill="y", side="left")
        
        self.create_menu_items()
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff")]
        )
        if file_path and 'on_file_open' in self.callbacks:
            self.callbacks['on_file_open'](file_path)
    
    def create_menu_items(self):
        menu_items = [
            { 'text': 'Open', 'command': self.open_file },
            { 'text': 'RGB', 'command': lambda: self.callbacks.get('on_rgb', lambda: print("RGB clicked"))() },
            { 'text': 'GrayScale', 'command': lambda: self.callbacks.get('on_gray_scale', lambda: print("GrayScale clicked"))() },
            { 'text': 'Settings', 'command': lambda: self.callbacks.get('on_settings', lambda: print("Settings clicked"))() },
            { 'text': 'Help', 'command': lambda: self.callbacks.get('on_help', lambda: print("Help clicked"))() }
        ]
        
        for item in menu_items:
            btn = ttk.Button(self, text=item['text'], command=item['command'], style='Custom.TButton')
            btn.pack(pady=2, padx=2, fill="x")
