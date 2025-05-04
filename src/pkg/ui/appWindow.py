import ttkbootstrap as ttk

from devopsnextgenx.components.StatusBar import StatusBar
from pkg.ui.menu.menuFrame import MenuFrame
from pkg.core.history.HistoryManager import HistoryManager
from pkg.core.imageProcessUtils import ImageProcessor
from pkg.core.history.TreePreviewComponent import TreePreviewComponent
from ttkbootstrap.constants import BOTH

class AppWindow(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")

        self.inputFile = None

        self.title("Component Demo")
        self.geometry("600x400")

        # Add status bar at the bottom
        self.status_bar = StatusBar(self, progress_thickness=5)
        self.status_bar.pack(fill="x", side="bottom", padx=10, pady=5)
        self.status_bar.update_user("Amit")
        self.status_bar.update_access("Admin")

        self.mainWindow = ttk.Frame(self)
        self.mainWindow.pack(fill="both", expand=True, padx=10, pady=10)

        # Add menu Frame to store menu items to the left
        self.menuFrame = MenuFrame(self.mainWindow, width=120,
                                    callbacks = {
                                       "on_file_open": self.load_image,
                                       "on_gray_scale": self.apply_grayscale,
                                       "on_rgb": self.apply_rgb
                                    })
        self.menuFrame.pack_propagate(False)  # Prevent frame from shrinking
        self.menuFrame.pack(side="left", fill="y")


        # Create a container frame for the main content
        self.content_frame = ttk.Frame(self.mainWindow)
        self.content_frame.pack(side="right", fill=BOTH, expand=True)

        # Add resize handle
        self.resize_frame = ttk.Frame(self.mainWindow, width=5, cursor="sb_h_double_arrow")
        self.resize_frame.pack(side="left", fill="y")
        
        # Add separator line
        self.separator = ttk.Separator(self.mainWindow, orient="vertical")
        self.separator.pack(side="left", fill="y", padx=2)

        # Get singleton instances instead of creating new ones
        self.image_processor = ImageProcessor()
        
        # Move treePreview into content_frame and ensure it fills properly
        self.treePreview = TreePreviewComponent(parent=self.content_frame, default_position="LEFT")
        self.treePreview.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Bind mouse events for resizing
        self.resize_frame.bind("<Button-1>", self.start_resize)
        self.resize_frame.bind("<B1-Motion>", self.do_resize)


    def start_resize(self, event):
        self.x = event.x
        self.initial_width = self.menuFrame.winfo_width()

    def do_resize(self, event):
        width_delta = event.x - self.x
        new_width = max(120, min(self.initial_width + width_delta, self.winfo_width() * 0.8))
        self.resize_component(self.menuFrame, new_width)

    def resize_component(self, component, new_width):
        """
        Generic function to resize any component horizontally
        
        Args:
            component: The frame/component to resize
            new_width: The new width to set
        """
        component.configure(width=new_width)

    def load_image(self, file_path):
        self.inputFile = file_path
        self.image_processor.load_image(file_path)
        self.treePreview.populate_tree(self.image_processor.history_manager.root_node)

    def apply_rgb(self):
        if not self.inputFile:
            return
        
        self.image_processor.convertBGR2RGB()
        self.treePreview.populate_tree(self.image_processor.history_manager.root_node)

    def apply_grayscale(self):
        if not self.inputFile:
            return
        
        self.image_processor.apply_grayscale()
        self.treePreview.populate_tree(self.image_processor.history_manager.root_node)
