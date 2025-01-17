import pytesseract
from PIL import Image
import argparse
import os

def perform_ocr(image_path, lang='eng'):
    """
    Performs OCR on the given image and returns the extracted text.
    
    Parameters:
    - image_path (str): Path to the input image.
    - lang (str): Language code for Tesseract OCR (default: 'eng').
    
    Returns:
    - str: Extracted text from the image.
    """
    try:
        # Open the image using Pillow
        img = Image.open(image_path)
        
        # Perform OCR using pytesseract
        text = pytesseract.image_to_string(img, lang=lang)
        
        return text.strip()
    except Exception as e:
        print(f"Error performing OCR on {image_path}: {e}")
        return None

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Perform OCR on an image using Tesseract.")
    parser.add_argument('image_path', type=str, help="Path to the input image file.")
    parser.add_argument('--lang', type=str, default='eng', help="Language code for Tesseract OCR (default: 'eng').")
    
    args = parser.parse_args()
    
    # Validate image path
    if not os.path.isfile(args.image_path):
        print(f"Error: File does not exist - {args.image_path}")
        return
    
    # Perform OCR
    extracted_text = perform_ocr(args.image_path, args.lang)
    
    if extracted_text:
        print("----- OCR Result -----")
        print(extracted_text)
    else:
        print("No text extracted or an error occurred.")

if __name__ == "__main__":
    main()
