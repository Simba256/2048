import os
import sys
import argparse
import pytesseract
from PIL import Image, ImageEnhance
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def adjust_brightness(img, brightness_factor):
    """
    Adjusts the brightness of an image.

    Parameters:
    - img (PIL.Image.Image): The input image.
    - brightness_factor (float): Brightness factor (>1 to brighten, <1 to darken).

    Returns:
    - PIL.Image.Image: The brightness-adjusted image.
    """
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(brightness_factor)

def adjust_contrast(img, contrast_factor):
    """
    Adjusts the contrast of an image.

    Parameters:
    - img (PIL.Image.Image): The input image.
    - contrast_factor (float): Contrast factor (>1 to increase, <1 to decrease).

    Returns:
    - PIL.Image.Image: The contrast-adjusted image.
    """
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(contrast_factor)

def binarize_image(img, threshold):
    """
    Binarizes an image based on a specified threshold.

    Parameters:
    - img (PIL.Image.Image): The input image.
    - threshold (int): Threshold value (0-255).

    Returns:
    - PIL.Image.Image: The binarized image.
    """
    if img.mode != 'L':
        img = img.convert('L')  # Ensure image is in grayscale
    binarized = img.point(lambda x: 255 if x > threshold else 0, '1')
    return binarized

def perform_ocr(img, lang='eng'):
    """
    Performs OCR on a processed image using Tesseract.

    Parameters:
    - img (PIL.Image.Image): The processed image.
    - lang (str): Language code for Tesseract OCR.

    Returns:
    - str: The OCR-extracted text.
    """
    # Configure Tesseract to recognize only digits
    custom_config = r'--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(img, config=custom_config, lang=lang)
    # Clean the text to retain only digits
    text = ''.join(filter(str.isdigit, text))
    return text

def process_image(image_path, brightness, contrast, threshold, lang='eng', save_processed=False, processed_dir=None):
    """
    Processes a single image with specified hyperparameters and returns OCR text.

    Parameters:
    - image_path (str): Path to the input image.
    - brightness (float): Brightness factor.
    - contrast (float): Contrast factor.
    - threshold (int): Binarization threshold.
    - lang (str): Language code for Tesseract OCR.
    - save_processed (bool): Whether to save the processed image.
    - processed_dir (str): Directory to save the processed image.

    Returns:
    - str: OCR-extracted text.
    """
    try:
        # Open the image
        img = Image.open(image_path)
        logging.info(f"Processing image: {image_path}")

        # Apply brightness adjustment
        img = adjust_brightness(img, brightness)
        logging.debug(f"Applied brightness factor: {brightness}")

        # Apply contrast adjustment
        img = adjust_contrast(img, contrast)
        logging.debug(f"Applied contrast factor: {contrast}")

        # Apply binarization
        img = binarize_image(img, threshold)
        logging.debug(f"Applied binarization threshold: {threshold}")

        # Optionally save the processed image
        if save_processed and processed_dir:
            if not os.path.exists(processed_dir):
                os.makedirs(processed_dir)
                logging.info(f"Created directory for processed images: {processed_dir}")
            processed_filename = f"processed_b{brightness}_c{contrast}_t{threshold}_{os.path.basename(image_path)}"
            processed_path = os.path.join(processed_dir, processed_filename)
            img.save(processed_path)
            logging.info(f"Saved processed image: {processed_path}")

        # Perform OCR
        ocr_text = perform_ocr(img, lang)
        logging.info(f"OCR Result: {ocr_text}")

        return ocr_text

    except Exception as e:
        logging.error(f"Error processing image {image_path}: {e}")
        return None

def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
    - argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Apply hyperparameters to an image and perform OCR using Tesseract.")
    parser.add_argument('image_path', type=str, help="Path to the input image.")
    parser.add_argument('--brightness', type=float, required=True, help="Brightness factor (>1 to brighten, <1 to darken).")
    parser.add_argument('--contrast', type=float, required=True, help="Contrast factor (>1 to increase, <1 to decrease).")
    parser.add_argument('--threshold', type=int, required=True, help="Binarization threshold (0-255).")
    parser.add_argument('--lang', type=str, default='eng', help="Language code for Tesseract OCR (default: 'eng').")
    parser.add_argument('--save', action='store_true', help="Save the processed image.")
    parser.add_argument('--output_dir', type=str, default=None, help="Directory to save the processed image (required if --save is used).")
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Validate image path
    if not os.path.isfile(args.image_path):
        logging.error(f"Image file does not exist: {args.image_path}")
        sys.exit(1)

    # Validate threshold
    if not (0 <= args.threshold <= 255):
        logging.error("Threshold must be between 0 and 255.")
        sys.exit(1)

    # If --save is used, ensure output_dir is provided
    if args.save and not args.output_dir:
        logging.error("Output directory must be specified with --output_dir when using --save.")
        sys.exit(1)

    # Perform processing and OCR
    ocr_text = process_image(
        image_path=args.image_path,
        brightness=args.brightness,
        contrast=args.contrast,
        threshold=args.threshold,
        lang=args.lang,
        save_processed=args.save,
        processed_dir=args.output_dir
    )

    if ocr_text is not None:
        print(f"OCR Text: {ocr_text}")
    else:
        print("OCR failed or an error occurred during processing.")

if __name__ == "__main__":
    main()
