import os
import cv2

def createOutputFolder(destination):
    if not os.path.exists(destination):
        os.makedirs(destination, exist_ok=True)

def saveImage(image, file_path = "image.png"):
    """
    Save the image to the specified file path.
    
    Args:
        image: The image to save.
        file_path: The path where the image will be saved.
    """
    file_path = os.path.join("output", file_path)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    cv2.imwrite(file_path, image)  # Assuming cv2 is already imported in the context where this function is used