import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import os
import sys
import argparse
import pandas as pd
from tqdm import tqdm

def load_image(image_path):
    """
    Loads an image from the specified path.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Warning: Unable to load image at {image_path}. Skipping.")
    return image

def preprocess_image(img, size=(300, 300)):
    """
    Converts image to grayscale and resizes it to the specified size.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, size)
    return resized

def calculate_ssim(img1, img2):
    """
    Calculates the Structural Similarity Index between two images.
    """
    score, _ = ssim(img1, img2, full=True)
    return score

def get_image_files(folder):
    """
    Retrieves a list of image file paths from the specified folder.
    """
    supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')
    files = [f for f in os.listdir(folder) if f.lower().endswith(supported_extensions)]
    return [os.path.join(folder, f) for f in files]

def main(set1_folder, set2_folder, output_csv=None, resize_dim=(300, 300)):
    # Get list of image files
    set1_images = get_image_files(set1_folder)
    set2_images = get_image_files(set2_folder)

    if not set1_images:
        print(f"No images found in {set1_folder}. Exiting.")
        sys.exit(1)
    if not set2_images:
        print(f"No images found in {set2_folder}. Exiting.")
        sys.exit(1)

    # Initialize similarity matrix
    similarity_matrix = pd.DataFrame(index=[os.path.basename(f) for f in set1_images],
                                     columns=[os.path.basename(f) for f in set2_images])

    # Iterate through each image pair and compute similarity
    print("Computing similarity scores...")
    for img1_path in tqdm(set1_images, desc="Set1 Images"):
        img1 = load_image(img1_path)
        if img1 is None:
            # Skip if image failed to load
            similarity_matrix.loc[os.path.basename(img1_path), :] = np.nan
            continue
        pre1 = preprocess_image(img1, size=resize_dim)

        for img2_path in set2_images:
            img2 = load_image(img2_path)
            if img2 is None:
                similarity = np.nan
            else:
                pre2 = preprocess_image(img2, size=resize_dim)
                similarity_score = calculate_ssim(pre1, pre2)
                similarity_percentage = similarity_score * 100
                similarity = round(similarity_percentage, 2)
            similarity_matrix.loc[os.path.basename(img1_path), os.path.basename(img2_path)] = similarity

    # Display the similarity matrix
    print("\nSimilarity Matrix (%):")
    print(similarity_matrix)

    # Optionally save to CSV
    if output_csv:
        similarity_matrix.to_csv(output_csv)
        print(f"\nSimilarity matrix saved to {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare similarity between images in two folders.")
    parser.add_argument("set1", help="Path to the first folder (set1).")
    parser.add_argument("set2", help="Path to the second folder (set2).")
    parser.add_argument("--output", "-o", help="Path to save the similarity matrix as CSV.", default=None)
    parser.add_argument("--resize", "-r", nargs=2, type=int, metavar=('width', 'height'),
                        help="Resize images to the specified width and height (default: 300x300).",
                        default=[300, 300])

    args = parser.parse_args()

    main(args.set1, args.set2, output_csv=args.output, resize_dim=tuple(args.resize))
