import os
import sys
import argparse
import pandas as pd
from tqdm import tqdm
import imagehash
from PIL import Image
import numpy as np

def get_image_files(folder):
    """
    Retrieves a list of image file paths from the specified folder.
    """
    supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')
    files = [f for f in os.listdir(folder) if f.lower().endswith(supported_extensions)]
    return [os.path.join(folder, f) for f in files]

def create_id_mapping(image_paths):
    """
    Creates a mapping from integer IDs to image file names.
    Returns a dictionary {id: filename} and a list of IDs.
    """
    id_to_filename = {}
    id_list = []
    for idx, path in enumerate(image_paths, start=1):
        filename = os.path.basename(path)
        id_to_filename[idx] = filename
        id_list.append(idx)
    return id_to_filename, id_list

def compute_hash(image_path, hash_func=imagehash.average_hash):
    """
    Computes the image hash using the specified hash function.
    """
    try:
        img = Image.open(image_path)
        return hash_func(img)
    except Exception as e:
        print(f"Warning: Unable to compute hash for {image_path}. Error: {e}")
        return None

def hamming_distance(hash1, hash2):
    """
    Computes the Hamming distance between two image hashes.
    """
    return hash1 - hash2  # imagehash library overloads the '-' operator for Hamming distance

def main(set1_folder, set2_folder, output_csv=None, hash_func=imagehash.average_hash):
    # Get list of image files
    set1_images = get_image_files(set1_folder)
    set2_images = get_image_files(set2_folder)

    if not set1_images:
        print(f"No images found in {set1_folder}. Exiting.")
        sys.exit(1)
    if not set2_images:
        print(f"No images found in {set2_folder}. Exiting.")
        sys.exit(1)

    # Create ID mappings
    set1_mapping, set1_ids = create_id_mapping(set1_images)
    set2_mapping, set2_ids = create_id_mapping(set2_images)

    # Precompute hashes
    print("Computing image hashes for Set1...")
    set1_hashes = {}
    for img_path, id1 in tqdm(zip(set1_images, set1_ids), total=len(set1_images), desc="Set1 Hashing"):
        img_hash = compute_hash(img_path, hash_func=hash_func)
        set1_hashes[id1] = img_hash

    print("Computing image hashes for Set2...")
    set2_hashes = {}
    for img_path, id2 in tqdm(zip(set2_images, set2_ids), total=len(set2_images), desc="Set2 Hashing"):
        img_hash = compute_hash(img_path, hash_func=hash_func)
        set2_hashes[id2] = img_hash

    # Initialize similarity matrix
    similarity_matrix = pd.DataFrame(
        index=set1_ids,
        columns=set2_ids,
        dtype=float
    )

    # Define similarity threshold (optional)
    # For example, maximum Hamming distance to consider as similar
    max_distance = 10  # Adjust based on hash size and requirements

    # Iterate through each image pair and compute similarity
    print("Computing similarity scores using Hamming distance...")
    for id1 in tqdm(set1_ids, desc="Set1 IDs"):
        hash1 = set1_hashes.get(id1)
        if hash1 is None:
            similarity_matrix.loc[id1, :] = np.nan
            continue

        for id2 in set2_ids:
            hash2 = set2_hashes.get(id2)
            if hash2 is None:
                similarity = np.nan
            else:
                distance = hamming_distance(hash1, hash2)
                # Convert distance to similarity percentage
                # Assuming hash size is 64 bits (for average_hash)
                similarity_percentage = (1 - (distance / len(hash1.hash) ** 2)) * 100
                similarity = round(similarity_percentage, 2)
            similarity_matrix.loc[id1, id2] = similarity

    # Display the similarity matrix
    print("\nSimilarity Matrix (%):")
    print(similarity_matrix)

    # Optionally save to CSV
    if output_csv:
        similarity_matrix.to_csv(output_csv)
        print(f"\nSimilarity matrix saved to {output_csv}")

        # Save ID mappings
        set1_map_df = pd.DataFrame(list(set1_mapping.items()), columns=['ID', 'Filename'])
        set2_map_df = pd.DataFrame(list(set2_mapping.items()), columns=['ID', 'Filename'])

        set1_mapping_csv = os.path.splitext(output_csv)[0] + "_set1_mapping.csv"
        set2_mapping_csv = os.path.splitext(output_csv)[0] + "_set2_mapping.csv"

        set1_map_df.to_csv(set1_mapping_csv, index=False)
        set2_map_df.to_csv(set2_mapping_csv, index=False)

        print(f"Set1 ID mapping saved to {set1_mapping_csv}")
        print(f"Set2 ID mapping saved to {set2_mapping_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare similarity between images in two folders using image hashing.")
    parser.add_argument("set1", help="Path to the first folder (set1).")
    parser.add_argument("set2", help="Path to the second folder (set2).")
    parser.add_argument("--output", "-o", help="Path to save the similarity matrix as CSV.", default=None)
    parser.add_argument("--hash", "-H", choices=['average', 'phash', 'dhash', 'whash'], default='average',
                        help="Hashing algorithm to use: 'average', 'phash', 'dhash', 'whash'. Default is 'average'.")

    args = parser.parse_args()

    # Select hash function based on user input
    hash_functions = {
        'average': imagehash.average_hash,
        'phash': imagehash.phash,
        'dhash': imagehash.dhash,
        'whash': imagehash.whash
    }

    selected_hash_func = hash_functions[args.hash]

    main(args.set1, args.set2, output_csv=args.output, hash_func=selected_hash_func)
