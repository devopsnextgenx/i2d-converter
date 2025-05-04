- create a ttkbootstrap Frame, to hold two components
- One component will be TreeComponent, Other will be PreviewComponent, positioned using one of LEFT,RIGHT,TOP,BOTTOM, use this position to place PreviewComponent in respect to TreeComponent
- Allow both component to start combinely take full parent height/width
- Resize of parent resize both TreeComponent and PreviewComponent
- PreviewComponent shows couple of labels and two images, one for input other for output, both image previews can also be positioned using LEFT,RIGHT,TOP,BOTTOM, for output image respect to input, show dropdown in Preview to allow change position of the InputPreview/OutputPreview 
- Resize of PreviewComponent resize InputPreview/OutputPreview
- On node selection from TreeComponent, show the data associated with node in PreviewComponent
- PreviewComponent shows the Image using path described in node using input_file, output_file usinv cv2 opencv and PIL
- Devider between TreeComponent and PreviewComponentcan be used to drag and resize
- Make TreeComponent hold tree in scroll container/frame
- Make sure we use below classes for defining above UI
    - TreePreviewComponent - Parent for both TreeComponent/PreviewComponent, refault position RIGHT to place PreviewComponent of TreeComponent
        - TreeComponent - holds the Tree functionality has ability to select single node
        - PreviewComponent - Holds, InputPreview/OutputPreview and ProcessDetailPreview, default position TOP for InputPreview of OutputPreview
            - Position InputPreview and OutputPreview in one ParentPreview frame, and position ProcessDetailPreview below ParentPreview
            - ImagePreview base class for InputPreview/OutputPreview, has ability to show image based on either path or image as MatLike
            - ProcessDetailPreview shows the details for the process with grid structure to iterate over list of attributes in node, and have a filter to decide which attributes to show with label and value

Use ttkbootstrap, customtkinter, opencv, PIL libraries

refer given image for getting 

Use below class for node/nodelist for populating the tree
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from PIL import Image, ImageTk
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
```


