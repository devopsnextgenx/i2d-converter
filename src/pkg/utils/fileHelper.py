import os

def createOutputFolder(destination):
    if not os.path.exists(destination):
        os.makedirs(destination, exist_ok=True)