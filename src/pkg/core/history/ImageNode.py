from PIL import Image, ImageTk
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

# Data classes for node/nodelist as provided
@dataclass
class ProcessingDetails:
    operation_name: str
    timestamp: datetime
    parameters: dict = None

class ImageNode:
    def __init__(self, input: any, output: any, operation_details: ProcessingDetails):
        self.input = input
        self.output = output
        self.operation_details = operation_details
        self.previous_node: Optional[ImageNode] = None
        self.next_nodes: List[ImageNode] = []

    def __repr__(self):
        return f"ImageNode(operation={self.operation_details.operation_name}, timestamp={self.operation_details.timestamp})"
    
    def __str__(self):
        return f"ImageNode(operation={self.operation_details.operation_name}, timestamp={self.operation_details.timestamp})"
    
    def set_input_file(self, input_file: str):
        """Set the input file for this node"""
        self.input_file = input_file

    def get_input_file(self) -> str:
        """Get the input file for this node"""
        return self.input_file if hasattr(self, 'input_file') else None
    
    def add_next_node(self, node: 'ImageNode'):
        """Add a new node as the next processing step"""
        node.previous_node = self
        self.next_nodes.append(node)
        
    def get_processing_chain(self) -> List[ProcessingDetails]:
        """Get the full chain of processing steps from start to this node"""
        chain = []
        current = self
        while current:
            chain.append(current.operation_details)
            current = current.previous_node
        return list(reversed(chain))

    def get_photo_preview(self, fw, fh):
        i_pil_image = Image.fromarray(self.input) if self.input is not None else None
        o_pil_image = Image.fromarray(self.output)
        
        output = ImageTk.PhotoImage(o_pil_image)
        """Get the photo preview for the current node"""
        input = ImageTk.PhotoImage(i_pil_image) if i_pil_image is not None else None
        return input, output
