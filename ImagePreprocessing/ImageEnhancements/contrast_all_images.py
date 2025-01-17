from PIL import Image, ImageEnhance
import os

# Define the directory containing images
input_dir = 'E:\\Basim\\Programming\\Automation\\2048\\brightened'
output_dir = os.path.join(input_dir, 'processed')

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each image in the input directory
for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp')):
        img_path = os.path.join(input_dir, filename)
        img = Image.open(img_path).convert('L')  # Convert to grayscale

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img_enhanced = enhancer.enhance(10.0)  # Adjust the factor as needed

        # Save the processed image
        output_path = os.path.join(output_dir, f'processed_{filename}')
        img_enhanced.save(output_path)
        print(f'Processed {filename} -> {output_path}')
