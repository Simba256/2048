from PIL import Image, ImageEnhance
import os

def adjust_brightness(input_path, output_path, factor):
    img = Image.open(input_path).convert('RGB')
    enhancer = ImageEnhance.Brightness(img)
    img_enhanced = enhancer.enhance(factor)  # Factor >1 brightens, <1 darkens
    img_enhanced.save(output_path)
    print(f"Processed and saved: {output_path}")

def process_directory(input_dir, output_dir, factor):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f'bright_{filename}')
            adjust_brightness(input_path, output_path, factor)

if __name__ == "__main__":
    input_directory = r'E:\Basim\Programming\Automation\2048'
    output_directory = os.path.join(input_directory, 'brightened')
    brightness_factor = 1  # >1 for brightening, <1 for darkening
    
    process_directory(input_directory, output_directory, brightness_factor)
    print("Batch processing complete.")
