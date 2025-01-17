from PIL import Image, ImageEnhance
import os
import numpy as np

def adjust_brightness(input_path, output_path, factor):
    """
    Adjusts the brightness of an image and saves the result.

    Parameters:
    - input_path (str): Path to the input image.
    - output_path (str): Path to save the adjusted image.
    - factor (float): Brightness factor. >1 to brighten, <1 to darken, 1 for original.
    """
    try:
        img = Image.open(input_path).convert('RGB')
        enhancer = ImageEnhance.Brightness(img)
        img_enhanced = enhancer.enhance(factor)
        img_enhanced.save(output_path)
        print(f"Processed and saved: {output_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def process_directory(input_dir, output_dir, start=0.00, end=10.00, step=0.01):
    """
    Processes all images in the input directory, adjusting brightness across a range of factors.

    Parameters:
    - input_dir (str): Directory containing input images.
    - output_dir (str): Directory to save processed images.
    - start (float): Starting brightness factor.
    - end (float): Ending brightness factor.
    - step (float): Increment step for brightness factor.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Generate brightness factors using numpy for precision
    brightness_factors = np.arange(start, end + step, step)
    brightness_factors = np.round(brightness_factors, 2)  # Round to 2 decimal places
    
    # Iterate over each image in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp')):
            input_path = os.path.join(input_dir, filename)
            name, ext = os.path.splitext(filename)
            
            # Iterate over each brightness factor
            for factor in brightness_factors:
                # Format the factor to two decimal places, replace '.' with '_' for filename
                factor_str = f"{factor:.2f}".replace('.', '_')
                output_filename = f"{name}_bright_{factor_str}{ext}"
                output_path = os.path.join(output_dir, output_filename)
                
                adjust_brightness(input_path, output_path, factor)

if __name__ == "__main__":
    # Define input and output directories
    input_directory = r'E:\Basim\Programming\Automation\2048'
    output_directory = os.path.join(input_directory, 'brightened')
    
    # Define brightness adjustment parameters
    brightness_start = 0.00   # Starting brightness factor
    brightness_end = 10.00    # Ending brightness factor
    brightness_step = 0.01    # Increment step
    
    print("Starting batch brightness adjustment...")
    process_directory(input_directory, output_directory, brightness_start, brightness_end, brightness_step)
    print("Batch processing complete.")
