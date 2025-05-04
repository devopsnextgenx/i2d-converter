set dotenv-load := false

default:
  @just --list --unsorted

testfile := '1.png'

prepare:
    pip3 --trusted-host pypi.python.org install numpy matplotlib keras-ocr tensorflow opencv-python pytesseract

dump file=testfile:
    py b2d/b2d.py dump test/data/{{file}} 

display file=testfile:
    py b2d/b2d.py display test/data/{{file}} 

displayAll:
    py b2d/b2d.py display

b2d file=testfile:
    py b2d/b2d.py both test/data/{{file}} 