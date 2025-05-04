from pkg.utils.Singleton import Singleton
from .history.HistoryManager import HistoryManager
import cv2

class ImageProcessor(metaclass=Singleton):
    def __init__(self, status_bar=None):
        # Initialize any required attributes
        self.history_manager = HistoryManager()
        self.status_bar = status_bar
        pass

    def update_status(self, message):
        """
        Update status bar with a message
        
        Args:
            message: Message to display in the status bar
        """
        if self.status_bar:
            self.status_bar.update_status(message)

    def load_image(self, file_path):
        """
        Load and resize image for display
        
        Args:
            file_path: Path to image file
            display_frame: Frame where image will be displayed
            update_callback: Optional callback for status updates
        
        Returns:
            tuple: (PIL PhotoImage, processed image)
        """
        # Read image using OpenCV
        self.history_manager.start_new_chain(file_path)
        self.update_status(f"Loaded image: {file_path}")
        return self.history_manager.current_node.output

    def convertBGR2RGB(self, image = None):
        """
        Convert BGR image to RGB format
        
        Args:
            image: Input image in BGR format
            
        Returns:
            tuple: (PIL PhotoImage, processed image)
        """
        image = image if image is not None else self.history_manager.get_active_node().output

        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        self.history_manager.add_processing_step(
            output=image,
            operation="RGB",
            parameters=None
        )
        self.update_status(f"Converted image to RGB format")
        return image

    def convertToGray(self, image = None):
        """
        Apply grayscale transformation to image
        
        Args:
            input_file: Path to input image
            
        Returns:
            tuple: (output file path, operation parameters)
        """
        image = image if image is not None else self.history_manager.get_active_node().output

        # Read image using OpenCV
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        self.history_manager.add_processing_step(
            output=image,
            operation="Grayscale"
        )

        return image