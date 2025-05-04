from ttkbootstrap.constants import BOTH, VERTICAL, HORIZONTAL, LEFT, RIGHT, TOP, BOTTOM, X, Y, PRIMARY, INFO, NW, W
from datetime import datetime
from tkinter import ttk
from typing import Literal
from PIL import Image, ImageTk

from ...core.history.HistoryManager import HistoryManager
from ...core.history.ImageNode import ImageNode, ProcessingDetails

import ttkbootstrap as tb
import tkinter as tk
import numpy as np
import cv2
import os

# Position type for component layout
Position = Literal["LEFT", "RIGHT", "TOP", "BOTTOM"]

class ImagePreview(tb.Frame):
    """Base class for displaying images"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.image_container = tb.Label(self)
        self.image_container.pack(fill=BOTH, expand=True)
        self.title_label = tb.Label(self, text="Image", font=("TkDefaultFont", 10, "bold"))
        self.title_label.pack(side=BOTTOM, fill=X)
        self.current_image = None
        self.photo_image = None
        
        # Bind to size changes
        self.bind("<Configure>", self._on_resize)
        
    def _on_resize(self, event):
        """Handle resize events"""
        # Only update if we have an image and the size actually changed
        if self.current_image is not None:
            self.update_display()
            
    def set_title(self, title: str):
        """Set the title of the image preview"""
        self.title_label.config(text=title)
        
    def set_image_from_path(self, path: str):
        """Set image from file path"""
        if path and os.path.exists(path):
            self.current_image = cv2.imread(path)
            if self.current_image is not None:
                self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
                self.update_display()
                
    def set_image_from_array(self, image_array):
        """Set image from numpy array (OpenCV/PIL compatible)"""
        if image_array is not None:
            self.current_image = image_array
            self.update_display()
        else:
            self.clear_image()
            
    def update_display(self):
        """Update the display with current image, resizing to fit the container"""
        container_w = self.image_container.winfo_width()
        container_h = self.image_container.winfo_height()
        
        # Default to widget size, but ensure we have some minimum
        if container_w <= 1:
            container_w = 300
        if container_h <= 1:
            container_h = 300

        if self.current_image is not None:
            h, w = self.current_image.shape[:2]
            
            # Calculate aspect ratio preserved scaling
            scale = min(container_w/w, container_h/h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            # Check if image is grayscale (2D) or color (3D)
            is_grayscale = len(self.current_image.shape) == 2
            
            # Resize image
            resized_img = cv2.resize(self.current_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            # Convert grayscale to RGB if needed
            if is_grayscale:
                resized_img = cv2.cvtColor(resized_img, cv2.COLOR_GRAY2RGB)
            
            # Calculate padding
            top = (container_h - new_h) // 2
            left = (container_w - new_w) // 2
            
            # Create black background of container size
            padded_img = np.zeros((container_h, container_w, 3), dtype=np.uint8)
            
            # Place resized image in center
            padded_img[top:top+new_h, left:left+new_w] = resized_img
        else:
            # Create black background matching container size exactly
            padded_img = np.zeros((container_h, container_w, 3), dtype=np.uint8)

        # Convert to PIL and create PhotoImage
        pil_img = Image.fromarray(padded_img)
        self.photo_image = ImageTk.PhotoImage(pil_img)
        
        # Update label
        self.image_container.config(image=self.photo_image)
            
    def clear_image(self):
        """Clear the displayed image"""
        self.image_container.config(image="")
        self.photo_image = None
        self.current_image = None


class InputPreview(ImagePreview):
    """Preview component for input image"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.set_title("Input")


class OutputPreview(ImagePreview):
    """Preview component for output image"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.set_title("Output")


class ProcessDetailPreview(tb.Frame):
    """Component to display process details"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title_label = tb.Label(self, text="Process Details", font=("TkDefaultFont", 12, "bold"))
        self.title_label.pack(fill=X, padx=5, pady=5)
        
        # Filter frame
        filter_frame = tb.Frame(self)
        filter_frame.pack(fill=X, padx=5, pady=5)
        tb.Label(filter_frame, text="Filter:").pack(side=LEFT)
        self.filter_entry = tb.Entry(filter_frame)
        self.filter_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.filter_entry.bind("<KeyRelease>", self.apply_filter)
        
        # Create scrollable frame for details
        self.canvas = tk.Canvas(self)
        scrollbar = tb.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.details_frame = tb.Frame(self.canvas)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.details_frame, anchor=NW)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.details_frame.bind('<Configure>', self._on_frame_configure)
        
        self.details = {}
        self.current_node = None
        
    def _on_canvas_configure(self, event):
        """Update the scrollregion when the canvas is resized"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        
    def _on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def display_details(self, node: ImageNode):
        """Display process details for a node"""
        # Clear existing details
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        if node is None:
            return
        
        # Display operation name
        op_frame = tb.Frame(self.details_frame)
        op_frame.pack(fill=X, padx=5, pady=2)
        tb.Label(op_frame, text="Operation:", width=15, anchor=W).pack(side=LEFT)
        tb.Label(op_frame, text=node.operation_details.operation_name).pack(side=LEFT, fill=X, expand=True)
        
        # Display timestamp
        time_frame = tb.Frame(self.details_frame)
        time_frame.pack(fill=X, padx=5, pady=2)
        tb.Label(time_frame, text="Timestamp:", width=15, anchor=W).pack(side=LEFT)
        tb.Label(time_frame, text=str(node.operation_details.timestamp)).pack(side=LEFT, fill=X, expand=True)
        
        # Display parameters if available
        if node.operation_details.parameters:
            params_label = tb.Label(self.details_frame, text="Parameters:", font=("TkDefaultFont", 10, "bold"))
            params_label.pack(anchor=W, padx=5, pady=2)
            
            # Create grid for parameters
            row = 0
            self.details = {}
            for key, value in node.operation_details.parameters.items():
                param_frame = tb.Frame(self.details_frame)
                param_frame.pack(fill=X, padx=5, pady=1)
                
                # Parameter name
                name_label = tb.Label(param_frame, text=f"{key}:", width=15, anchor=W)
                name_label.pack(side=LEFT)
                
                # Parameter value
                value_label = tb.Label(param_frame, text=str(value))
                value_label.pack(side=LEFT, fill=X, expand=True)
                
                self.details[key] = (param_frame, name_label, value_label)
                row += 1
        
        # Save current node details for filtering
        self.current_node = node
        
    def apply_filter(self, event=None):
        """Apply filter to the details based on user input"""
        if not hasattr(self, 'details') or not self.details:
            return
            
        filter_text = self.filter_entry.get().lower()
        
        for key, (frame, name_label, value_label) in self.details.items():
            if filter_text in key.lower() or filter_text in str(value_label.cget("text")).lower():
                frame.pack(fill=X, padx=5, pady=1)
            else:
                frame.pack_forget()


class PreviewComponent(tb.Frame):
    def __init__(self, master, default_preview_position: Position = "RIGHT", **kwargs):
        super().__init__(master, **kwargs)
        self.preview_position = default_preview_position
        
        # Create position selector
        position_frame = tb.Frame(self)
        position_frame.pack(fill=X, padx=5, pady=5)
        tb.Label(position_frame, text="Preview Layout:").pack(side=LEFT)
        
        self.position_var = tk.StringVar(value=self.preview_position)
        position_dropdown = tb.Combobox(position_frame, textvariable=self.position_var, 
                                    values=["RIGHT", "BOTTOM"],
                                    state="readonly", width=10)
        position_dropdown.pack(side=RIGHT, padx=5)
        position_dropdown.bind("<<ComboboxSelected>>", self.update_preview_layout)
        
        # Create preview container
        self.preview_container = tb.Frame(self)
        self.preview_container.pack(fill=BOTH, expand=True)
        
        # Initialize preview components
        self.create_preview_components()
        
        # Bind to window resize events
        self.bind("<Configure>", self._on_main_resize)
        
    def _on_main_resize(self, event):
        """Handle resize of the main component"""
        # Only respond to size changes in this widget (not child widgets)
        if event.widget == self:
            # Update sash positions after resize
            self._update_sash_positions()
            
    def _update_sash_positions(self):
        """Update sash positions based on current container size"""
        if hasattr(self, 'main_paned') and self.main_paned.winfo_ismapped():
            # Set vertical split between previews and details (70/30)
            main_height = self.main_paned.winfo_height()
            if main_height > 20:  # Only set if we have some reasonable height
                self.main_paned.sashpos(0, int(main_height * 0.7))
            
        if hasattr(self, 'preview_paned') and self.preview_paned.winfo_ismapped():
            # Set horizontal/vertical split between input/output previews (50/50)
            if self.position_var.get() in ["LEFT", "RIGHT"]:
                width = self.preview_paned.winfo_width()
                if width > 20:  # Only set if we have some reasonable width
                    self.preview_paned.sashpos(0, width // 2)
            else:
                height = self.preview_paned.winfo_height()
                if height > 20:  # Only set if we have some reasonable height
                    self.preview_paned.sashpos(0, height // 2)
        
    def create_preview_components(self):
        """Create or recreate the preview components"""
        # Clear existing components
        for widget in self.preview_container.winfo_children():
            widget.destroy()
            
        # Create main vertical paned window to split preview and details
        self.main_paned = ttk.PanedWindow(self.preview_container, orient=tk.VERTICAL)
        self.main_paned.pack(fill=BOTH, expand=True)
        
        # Create horizontal/vertical paned window for input/output previews
        style = ttk.Style()
        style.configure('Preview.TPanedwindow', sashwidth=4, sashrelief='raised')
        
        # Set orientation based on position
        orient = tk.HORIZONTAL if self.position_var.get() in ["LEFT", "RIGHT"] else tk.VERTICAL
        self.preview_paned = ttk.PanedWindow(self.main_paned, orient=orient, style='Preview.TPanedwindow')
        
        # Get container dimensions
        container_width = self.preview_container.winfo_width()
        container_height = self.preview_container.winfo_height()
        
        # Use 48% of container size for each preview frame
        frame_width = max(int(container_width * 0.48), 300)
        frame_height = max(int(container_height * 0.48), 300)
        
        # Create frames with minimum sizes
        input_frame = tb.Frame(self.preview_paned, width=frame_width, height=frame_height)
        output_frame = tb.Frame(self.preview_paned, width=frame_width, height=frame_height)
        
        # Prevent frames from shrinking below minimum size
        input_frame.pack_propagate(False)
        output_frame.pack_propagate(False)
        
        # Create new preview components inside the fixed-size frames
        self.input_preview = InputPreview(input_frame, bootstyle=INFO)
        self.input_preview.pack(fill=BOTH, expand=True)
        
        self.output_preview = OutputPreview(output_frame, bootstyle=INFO)
        self.output_preview.pack(fill=BOTH, expand=True)
        
        # Add frames to preview paned window
        self.preview_paned.add(input_frame)
        self.preview_paned.add(output_frame)
        
        # Create process details preview
        if hasattr(self, 'process_detail_preview'):
            self.process_detail_preview.destroy()
        self.process_detail_preview = ProcessDetailPreview(self.main_paned)
        
        # Add components to main paned window
        self.main_paned.add(self.preview_paned, weight=7)  # 70% height
        self.main_paned.add(self.process_detail_preview, weight=3)  # 30% height
        
        # Update sash positions after widget is drawn
        self.after_idle(self._update_sash_positions)
        
    def update_preview_layout(self, event=None):
        """Update the layout of the preview components"""
        # Store current node if any process details are displayed
        current_node = None
        if hasattr(self, 'process_detail_preview') and hasattr(self.process_detail_preview, 'current_node'):
            current_node = self.process_detail_preview.current_node
        
        # Recreate components with new layout
        self.create_preview_components()
        
        # Reload the node data if we had any
        if current_node:
            self.display_node(current_node)
            
    def display_node(self, node: ImageNode):
        """Display the selected node's data"""
        if node is None:
            return
            
        # Update image previews
        if node.input is not None:
            self.input_preview.set_image_from_array(node.input)
        # elif hasattr(node, 'input_file') and node.input_file:
        #     self.input_preview.set_image_from_path(node.input_file)
        else:
            self.input_preview.clear_image()
            
        if node.output is not None:
            self.output_preview.set_image_from_array(node.output)
        # elif hasattr(node, 'output_file') and node.output_file:
        #     self.output_preview.set_image_from_path(node.output_file)
        else:
            self.output_preview.clear_image()
            
        # Update process details
        self.process_detail_preview.display_details(node)


class TreeComponent(tb.Frame):
    """Component to display the processing tree"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create a label for the tree
        self.title_label = tb.Label(self, text="Processing Tree", font=("TkDefaultFont", 12, "bold"))
        self.title_label.pack(fill=X, padx=5, pady=5)
        
        # Create scrollable treeview
        self.tree_frame = tb.Frame(self)
        self.tree_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Create scrollbars
        self.tree_y_scroll = tb.Scrollbar(self.tree_frame, orient=VERTICAL)
        self.tree_x_scroll = tb.Scrollbar(self.tree_frame, orient=HORIZONTAL)
        
        # Create treeview with indent of 20 pixels
        self.tree = ttk.Treeview(self.tree_frame, 
                                yscrollcommand=self.tree_y_scroll.set,
                                xscrollcommand=self.tree_x_scroll.set,
                                selectmode='browse',
                                style='Custom.Treeview')
        
        # Configure style for treeview indentation
        style = ttk.Style()
        style.configure('Custom.Treeview', indent=20)
        
        # Configure scrollbars
        self.tree_y_scroll.config(command=self.tree.yview)
        self.tree_x_scroll.config(command=self.tree.xview)
        
        # Arrange components
        self.tree_y_scroll.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=TOP, fill=BOTH, expand=True)
        self.tree_x_scroll.pack(side=BOTTOM, fill=X)
        
        # Configure tree columns - move operation to first column (#0)
        self.tree["columns"] = ("timestamp",)
        self.tree.column("#0", width=250, minwidth=200, stretch=True)  # Operation column
        self.tree.column("timestamp", width=180, minwidth=120, stretch=False)
        
        self.tree.heading("#0", text="Operation", anchor=W)  # Operation heading
        self.tree.heading("timestamp", text="Timestamp", anchor=W)
        
        # Store nodes
        self.nodes = {}
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)
        self.selection_callback = None
        
    def set_selection_callback(self, callback):
        """Set callback function for tree selection"""
        self.selection_callback = callback
        
    def on_item_selected(self, event):
        """Handle tree item selection"""
        selected_items = self.tree.selection()
        if selected_items and self.selection_callback:
            item_id = selected_items[0]
            if item_id in self.nodes:
                self.selection_callback(self.nodes[item_id])
                
    def add_node(self, node: ImageNode, parent_id=""):
        """Add a node to the tree"""
        # Create unique ID for the node
        node_id = f"node_{id(node)}"
        
        # Add to treeview - now with operation name in text field
        tree_id = self.tree.insert(
            parent_id, "end", 
            iid=node_id,
            text=node.operation_details.operation_name,  # Operation name as text
            values=(node.operation_details.timestamp.strftime("%Y-%m-%d %H:%M:%S"),)  # Timestamp only
        )
        
        # Store node reference
        self.nodes[node_id] = node
        
        # Add child nodes recursively
        for child_node in node.next_nodes:
            self.add_node(child_node, node_id)
            
        return node_id
        
    def populate_tree(self, root_node: ImageNode):
        """Populate the tree from a root node"""
        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.nodes = {}
        
        # Add root node and recursively add children
        if root_node:
            root_id = self.add_node(root_node)
            # Expand root node
            self.tree.item(root_id, open=True)
            # Select root node
            self.tree.selection_set(root_id)
            # Trigger selection event
            self.on_item_selected(None)


class TreePreviewComponent(tb.Frame):
    def __init__(self, parent, default_position="LEFT"):
        # Initialize the parent Frame class first
        super().__init__(parent)
        self.history_manager = HistoryManager()
        self.parent = parent  # Store parent reference
        self.position = default_position
        self.history_manager = HistoryManager()
        
        # Create paned window for resizable components
        self.paned_window = ttk.PanedWindow(
            self,  # Changed from parent to self since we are now a Frame
            orient=tk.HORIZONTAL if default_position in ["LEFT", "RIGHT"] else tk.VERTICAL
        )
        self.paned_window.pack(fill=BOTH, expand=True)
        
        # Create tree component with minimum size
        self.tree_component = TreeComponent(self.paned_window, bootstyle=PRIMARY)
        self.tree_component.configure(width=200)  # Minimum width
        
        # Create preview component with minimum size
        self.preview_component = PreviewComponent(self.paned_window, bootstyle=INFO)
        self.preview_component.configure(width=400)  # Minimum width
        
        # Set up tree selection callback
        self.tree_component.set_selection_callback(self.on_node_selected)
        
        # Add components to paned window based on position
        self.update_layout()
        
        # Bind to resize events on the paned_window instead
        self.paned_window.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Handle resize events"""
        # Only respond to size changes in this widget (not child widgets)
        if event.widget == self:
            self._update_sash_position()

    def _update_sash_position(self):
        """Update sash position based on current container size"""
        if not self.paned_window.winfo_ismapped():
            return
            
        # Get current size
        width = self.paned_window.winfo_width()
        height = self.paned_window.winfo_height()
        
        # Calculate 35% position based on orientation
        if self.position in ["LEFT", "RIGHT"]:
            if width > 20:
                # Set tree to 35% of width
                tree_width = int(width * 0.35)
                if self.position == "LEFT":
                    self.paned_window.sashpos(0, tree_width)
                else:  # RIGHT
                    self.paned_window.sashpos(0, int(width * 0.65))
        else:  # "TOP", "BOTTOM"
            if height > 20:
                # Set tree to 35% of height
                tree_height = int(height * 0.35)
                if self.position == "TOP":
                    self.paned_window.sashpos(0, tree_height)
                else:  # BOTTOM
                    self.paned_window.sashpos(0, int(height * 0.65))

    def update_layout(self):
        """Update the layout based on position"""
        # Remove existing panes
        for pane in self.paned_window.panes():
            self.paned_window.forget(pane)

        # Add components in correct order with appropriate weights
        if self.position in ["RIGHT", "BOTTOM"]:
            self.paned_window.add(self.tree_component, weight=35)
            self.paned_window.add(self.preview_component, weight=65)
        else:  # "LEFT", "TOP"
            self.paned_window.add(self.preview_component, weight=65)
            self.paned_window.add(self.tree_component, weight=35)

        # Update sash position after component layout using the paned_window
        self.paned_window.after_idle(self._update_sash_position)
            
    def set_position(self, position: Position):
        """Set the position of the preview component relative to tree"""
        if position != self.position:
            self.position = position
            self.update_layout()
            
    def on_node_selected(self, node: ImageNode):
        """Handle node selection in the tree"""
        self.preview_component.display_node(node)
        self.history_manager.set_selected_node(node)
        
    def populate_tree(self, root_node: ImageNode):
        """Populate the tree with nodes"""
        self.tree_component.populate_tree(root_node)

    def on_tree_select(self, event):
        selected_item = self.tree_component.tree.selection()
        if selected_item:
            node = self.tree_component.tree.item(selected_item[0], "values")[0]  # Get node from tree item
            self.history_manager.set_selected_node(node)
            # Update preview with selected node's image
            self.update_preview(node.output)

def create_sample_data():
    # Create a grayscale version for the output
    sample_load = cv2.imread("/home/kira/git/amitkshirsagar13/i2d-converter/sara.jpg")
    sample_rgb = cv2.cvtColor(sample_load, cv2.COLOR_BGR2RGB)
    sample_gray = cv2.cvtColor(sample_rgb, cv2.COLOR_RGB2GRAY)
    
    root_node = ImageNode(
        input=None,  # First node has no input
        output=sample_load,
        operation_details=ProcessingDetails(
            operation_name="BGR-Load",
            timestamp=datetime.now(),
            parameters={"width": 300, "height": 300, "channels": 3}
        )
    )
    
    rgb_node = ImageNode(
        input=sample_load,
        output=sample_rgb,
        operation_details=ProcessingDetails(
            operation_name="RGB",
            timestamp=datetime.now(),
            parameters={"copies": 2, "spacing": 100}
        )
    )
    root_node.add_next_node(rgb_node)
    
    # Add a grayscale processing node
    grayscale_node = ImageNode(
        input=sample_rgb,
        output=sample_gray,
        operation_details=ProcessingDetails(
            operation_name="GrayScale",
            timestamp=datetime.now(),
            parameters={"method": "luminance", "preserve_color_space": True}
        )
    )
    rgb_node.add_next_node(grayscale_node)
    
    return root_node

# Example usage
if __name__ == "__main__":
    # Create sample data

    # Create example application
    root = tb.Window(themename="darkly")
    root.title("Image Processing Tree")
    root.geometry("1000x600")
    
    # Create TreePreviewComponent
    tree_preview = TreePreviewComponent(root, default_position="LEFT")
    tree_preview.pack(fill=BOTH, expand=True)
    
    # Populate with sample data
    sample_root_node = create_sample_data()
    tree_preview.populate_tree(sample_root_node)
    
    root.mainloop()