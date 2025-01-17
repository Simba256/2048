import os
import pytesseract
from PIL import Image, ImageEnhance
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import itertools
import logging
import re

# Configure logging
logging.basicConfig(
    filename='hyperparameter_search.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def adjust_brightness(img, brightness_factor):
    """
    Adjusts the brightness of an image.
    """
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(brightness_factor)

def adjust_contrast(img, contrast_factor):
    """
    Adjusts the contrast of an image.
    """
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(contrast_factor)

def binarize_image(img, threshold):
    """
    Binarizes an image based on a threshold.
    """
    # Convert to grayscale if not already
    if img.mode != 'L':
        img = img.convert('L')
    # Apply threshold
    return img.point(lambda x: 255 if x > threshold else 0, '1')

def perform_ocr(img):
    """
    Performs OCR on an image using Tesseract.
    """
    # Configure Tesseract to recognize only digits
    custom_config = r'--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(img, config=custom_config)
    # Clean the text to retain only digits
    text = ''.join(filter(str.isdigit, text))
    return text

def extract_number_from_filename(filename):
    """
    Extracts the numerical value from filenames like 'tile_2.png'.
    Uses regex to handle unexpected formats gracefully.
    """
    match = re.search(r'tile_(\d+)', filename, re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        logging.warning(f"Filename does not match pattern 'tile_<number>.<ext>': {filename}")
        return None
    
def first_digit(num):
    """
    Returns the first digit of a number.
    """
    return int(str(num)[0])

def process_image(args):
    """
    Processes a single image with given parameters and checks OCR accuracy.
    Returns True if OCR matches the expected value, else False.
    Logs the result for each image.
    """
    image_path, expected_value, brightness, contrast, threshold = args
    try:
        img = Image.open(image_path)
        img = adjust_brightness(img, brightness)
        img = adjust_contrast(img, contrast)
        img = binarize_image(img, threshold)
        ocr_result = perform_ocr(img)
        
        if ocr_result == expected_value:
            logging.info(f"SUCCESS: {os.path.basename(image_path)} | B:{brightness} C:{contrast} T:{threshold} | OCR:{ocr_result}")
            return True
        else:
            logging.info(f"FAILURE: {os.path.basename(image_path)} | B:{brightness} C:{contrast} T:{threshold} | OCR:{ocr_result} | Expected:{expected_value}")
            return False
    except Exception as e:
        logging.error(f"ERROR processing {os.path.basename(image_path)} | B:{brightness} C:{contrast} T:{threshold} | Exception: {e}")
        return False

def test_combination(args):
    """
    Tests a single parameter combination across all images.
    Returns the parameters if all OCRs match, else None.
    """
    brightness, contrast, threshold, images = args
    for image_path, expected_value in images:
        if first_digit(expected_value)<3:
            continue
        result = process_image((image_path, expected_value, brightness, contrast, threshold))
        if not result:
            return None  # Early termination if any image fails
    return (brightness, contrast, threshold)

def find_successful_parameters(input_dir, brightness_values, contrast_values, threshold_values):
    """
    Finds all combinations of brightness, contrast, and threshold that result in correct OCR for all images.
    """
    # Gather all image files and their expected values
    images = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp')):
            expected_number = extract_number_from_filename(filename)
            if expected_number is not None:
                images.append((os.path.join(input_dir, filename), expected_number))
    
    total_images = len(images)
    print(f"Total images found: {total_images}")
    logging.info(f"Total images found: {total_images}")
    
    if total_images == 0:
        print("No valid images found in the specified directory.")
        logging.warning("No valid images found in the specified directory.")
        return []
    
    # Generate all parameter combinations
    parameter_combinations = list(itertools.product(brightness_values, contrast_values, threshold_values))
    total_combinations = len(parameter_combinations)
    print(f"Total parameter combinations to test: {total_combinations}")
    logging.info(f"Total parameter combinations to test: {total_combinations}")
    
    # Prepare arguments for Pool
    # Each argument is a tuple: (brightness, contrast, threshold, images)
    args_list = [(b, c, t, images) for (b, c, t) in parameter_combinations]
    
    # Define successful parameter list
    successful_parameters = []
    
    # Use multiprocessing Pool for parallel testing
    pool = Pool(processes=cpu_count()-1 or 1)  # Reserve one CPU core
    
    print("Starting parameter testing...")
    logging.info("Starting parameter testing...")
    
    # Iterate with tqdm progress bar
    for res in tqdm(pool.imap_unordered(test_combination, args_list), total=total_combinations):
        if res is not None:
            successful_parameters.append(res)
            logging.info(f"COMBINATION PASSED: B:{res[0]} C:{res[1]} T:{res[2]}")
    
    pool.close()
    pool.join()
    
    return successful_parameters

def main():
    # Define the input directory containing the images
    input_directory = r'E:\Basim\Programming\Automation\2048\tiles'  # Update this path as needed
    
    # Define the ranges for preprocessing parameters
    # Adjust the ranges and steps based on your requirements and computational resources
    brightness_start = 1.4
    brightness_end = 1.6
    brightness_step = 0.01
    brightness_values = np.arange(brightness_start, brightness_end + brightness_step, brightness_step).round(2).tolist()
    
    contrast_start = 0.0
    contrast_end = 10.0
    contrast_step = 0.1
    contrast_values = np.arange(contrast_start, contrast_end + contrast_step, contrast_step).round(2).tolist()
    
    threshold_start = 250
    threshold_end = 255
    threshold_step = 0.1
    threshold_values = np.arange(threshold_start, threshold_end + threshold_step, threshold_step).round(2).tolist()
    # list(range(threshold_start, threshold_end + threshold_step, threshold_step))
    
    print("Brightness values:", brightness_values)
    print("Contrast values:", contrast_values)
    print("Threshold values:", threshold_values)
    
    logging.info(f"Brightness values: {brightness_values}")
    logging.info(f"Contrast values: {contrast_values}")
    logging.info(f"Threshold values: {threshold_values}")
    
    # Find successful parameter combinations
    successful_params = find_successful_parameters(input_directory, brightness_values, contrast_values, threshold_values)
    
    # Print the successful combinations
    if successful_params:
        print("\nSuccessful Parameter Combinations:")
        logging.info("Successful Parameter Combinations:")
        for params in successful_params:
            brightness, contrast, threshold = params
            print(f"Brightness: {brightness}, Contrast: {contrast}, Threshold: {threshold}")
            logging.info(f"Brightness: {brightness}, Contrast: {contrast}, Threshold: {threshold}")
    else:
        print("\nNo successful parameter combinations found.")
        logging.info("No successful parameter combinations found.")

if __name__ == "__main__":
    main()
