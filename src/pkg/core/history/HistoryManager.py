from datetime import datetime
from typing import Optional
from pkg.utils.Singleton import Singleton
from .ImageNode import ImageNode, ProcessingDetails
import cv2

class HistoryManager(metaclass=Singleton):
    def __init__(self):
        self.root_node: Optional[ImageNode] = None
        self.current_node: Optional[ImageNode] = None
        self.selected_node: Optional[ImageNode] = None  # New attribute to track selected node
    
    def start_new_chain(self, input_file: str):
        """Initialize a new processing chain with original input file"""
        details = ProcessingDetails(
            operation_name="Original",
            timestamp=datetime.now()
        )
        output = cv2.imread(input_file)
        # Create the root node with the original image
        self.root_node = ImageNode(input=None, output=output, operation_details=details)
        self.root_node.set_input_file(input_file)
        self.current_node = self.root_node
        self.selected_node = self.root_node  # Initialize selected node
        
    def add_processing_step(self, output: any, operation: str, parameters: dict = None):
        """Add a new processing step to the chain"""
        if not self.current_node:
            raise ValueError("No active processing chain")
            
        parent_node = self.selected_node or self.current_node  # Create new node using current or selected node as parent
        details = ProcessingDetails(
            operation_name=operation,
            timestamp=datetime.now(),
            parameters=parameters
        )
        
        new_node = ImageNode(
            input=parent_node.output,
            output=output,
            operation_details=details
        )
        
        parent_node.add_next_node(new_node)
        self.current_node = new_node
        self.selected_node = new_node  # Update selected node
        
    def get_current_chain(self):
        """Get the current processing chain"""
        if self.current_node:
            return self.current_node.get_processing_chain()
        return []
    
    def set_selected_node(self, node: ImageNode):
        """Set the currently selected node in the history tree"""
        self.selected_node = node
    
    def get_active_node(self):
        """Get the node that should be used for processing (selected or current)"""
        return self.selected_node or self.current_node
    
    def clear_selection(self):
        """Clear the node selection, fallback to current_node"""
        self.selected_node = None