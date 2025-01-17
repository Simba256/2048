from PIL import Image, ImageEnhance
import os
import numpy as np
from tqdm import tqdm  # Optional: For progress bars

def adjust_brightness(input_path, output_path, brightness_factor):
    """
    Adjusts the brightness of an image and saves the result.

    Parameters:
    - input_path (str): Path to the input image.
    - output_path (str): Path to save the adjusted image.
    - brightness_factor (float): Brightness factor. >1 to increase, <1 to decrease.
    """
    try:
        img = Image.open(input_path).convert('RGB')
        enhancer = ImageEnhance.Brightness(img)
        img_bright = enhancer.enhance(brightness_factor)
        img_bright.save(output_path)
        print(f"Brightness adjusted and saved: {output_path}")
    except Exception as e:
        print(f"Error adjusting brightness for {input_path}: {e}")

def adjust_contrast(input_path, output_path, contrast_factor):
    """
    Adjusts the contrast of an image and saves the result.

    Parameters:
    - input_path (str): Path to the input image.
    - output_path (str): Path to save the adjusted image.
    - contrast_factor (float): Contrast factor. >1 to increase, <1 to decrease.
    """
    try:
        img = Image.open(input_path).convert('L')  # Convert to grayscale
        enhancer = ImageEnhance.Contrast(img)
        img_contrast = enhancer.enhance(contrast_factor)
        img_contrast.save(output_path)
        print(f"Contrast adjusted and saved: {output_path}")
    except Exception as e:
        print(f"Error adjusting contrast for {input_path}: {e}")

def binarize_image(input_path, output_path, threshold):
    """
    Binarizes an image based on a specified threshold.

    Parameters:
    - input_path (str): Path to the input image.
    - output_path (str): Path to save the binarized image.
    - threshold (int): Threshold value (0-255).
    """
    try:
        img = Image.open(input_path).convert('L')  # Convert to grayscale

        # Define the binarization function
        binarize = lambda x: 255 if x > threshold else 0

        # Apply the function to each pixel
        img_binarized = img.point(binarize, mode='1')  # '1' for 1-bit pixels

        img_binarized.save(output_path)
        print(f"Binarized image saved: {output_path}")
    except Exception as e:
        print(f"Error binarizing image {input_path}: {e}")

def process_directory(input_dir, output_dir, brightness_factor, contrast_factor, threshold):
    """
    Processes all images in the input directory by adjusting brightness, contrast, and binarizing.

    Parameters:
    - input_dir (str): Directory containing input images.
    - output_dir (str): Directory to save processed images.
    - brightness_factor (float): Factor to adjust brightness.
    - contrast_factor (float): Factor to adjust contrast.
    - threshold (int): Threshold value for binarization.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Get list of image files
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp'))]

    # Iterate over images with a progress bar
    for filename in tqdm(image_files, desc="Processing Images"):
        input_path = os.path.join(input_dir, filename)
        # Define intermediate paths
        bright_path = os.path.join(output_dir, f"bright_{filename}")
        contrast_path = os.path.join(output_dir, f"contrast_{filename}")
        binarized_path = os.path.join(output_dir, f"binarized_{filename}")

        # Adjust brightness
        adjust_brightness(input_path, bright_path, brightness_factor)

        # Adjust contrast
        adjust_contrast(bright_path, contrast_path, contrast_factor)

        # Binarize
        binarize_image(contrast_path, binarized_path, threshold)

    print("Batch processing complete.")

if __name__ == "__main__":
    # Define input and output directories
    input_directory = r'E:\Basim\Programming\Automation\2048'
    output_directory = os.path.join(input_directory, 'processed')

    # Define adjustment parameters
    brightness_factor = 1.2   # >1 to brighten, <1 to darken
    contrast_factor = 2.0     # >1 to increase contrast, <1 to decrease
    threshold_value = 128     # 0-255, adjust as needed

    process_directory(input_directory, output_directory, brightness_factor, contrast_factor, threshold_value)
