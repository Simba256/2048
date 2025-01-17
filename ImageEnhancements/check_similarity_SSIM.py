import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import argparse
import sys

def load_image(image_path):
    """
    Loads an image from the specified path.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        sys.exit(1)
    return image

def preprocess_images(img1, img2):
    """
    Converts images to grayscale and resizes them to the same dimensions.
    """
    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Resize images to the smallest dimensions among the two
    height = min(gray1.shape[0], gray2.shape[0])
    width = min(gray1.shape[1], gray2.shape[1])

    gray1_resized = cv2.resize(gray1, (width, height))
    gray2_resized = cv2.resize(gray2, (width, height))

    return gray1_resized, gray2_resized

def calculate_ssim(img1, img2):
    """
    Calculates the Structural Similarity Index between two images.
    """
    score, diff = ssim(img1, img2, full=True)
    return score

def main(image_path1, image_path2):
    # Load images
    img1 = load_image(image_path1)
    img2 = load_image(image_path2)

    # Preprocess images
    gray1, gray2 = preprocess_images(img1, img2)

    # Calculate SSIM
    similarity_score = calculate_ssim(gray1, gray2)

    # Convert to percentage
    similarity_percentage = similarity_score * 100

    print(f"Similarity: {similarity_percentage:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare similarity between two images.")
    parser.add_argument("image1", help="Path to the first image.")
    parser.add_argument("image2", help="Path to the second image.")

    args = parser.parse_args()

    main(args.image1, args.image2)
