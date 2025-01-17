# main.py

import logging
import argparse
import copy
import cv2
from image_similarity import load_images_from_folder, find_similar_images_for_references
from cell_images import capture_cell_images
import os
import time
from typing import Tuple, List, Optional
import numpy as np
from logger import setup_logging  # Assumes you have a separate logger.py
from game import next_board  # Assumes you have a game.py with next_board function


def is_board_filled_with_ones(board: List[List[int]]) -> bool:
    """
    Checks if the entire board is filled with 1s.

    Parameters:
        board (List[List[int]]): The game board.

    Returns:
        bool: True if all cells are 1, False otherwise.
    """
    for row in board:
        for cell in row:
            if cell != 1:
                return False
    return True


def get_all_power_of_two_filenames(folder_images: List[Tuple[int, str, Optional[np.ndarray]]]) -> List[str]:
    """
    Extracts filenames that are powers of two (e.g., '1.png', '2.png', ..., '16384.png').

    Parameters:
        folder_images (List[Tuple[int, str, Optional[np.ndarray]]]): 
            List of tuples containing (ID, filename, image) from the folder.

    Returns:
        List[str]: Filenames that represent powers of two.
    """
    power_of_two_filenames = []
    for (id, filename, image) in folder_images:
        basename = os.path.splitext(filename.lower())[0]
        if basename.isdigit():
            value = int(basename)
            if value & (value - 1) == 0 and value != 0:  # Check if power of two
                power_of_two_filenames.append(filename.lower())
    return power_of_two_filenames


def main(
    comparison_folder: str = 'teal_tiles',
    region: Tuple[int, int, int, int] = (688, 299, 494, 495),  # EMULATOR_REGION by default
    rows: int = 4,
    cols: int = 4,
    delay: int = 5,
    threshold: float = 0.95,
    resize_dim: Tuple[int, int] = (300, 300),
    grayscale: bool = True,
    use_parallel: bool = False,
    max_workers: int = 8,
    enable_logging: bool = True,  # New parameter to control logging
    new_board: List[List[int]] = [[1 for _ in range(4)] for _ in range(4)]
) -> List[List[int]]:
    """
    Captures cell images from the screen, preprocesses them, and finds similar images
    in the specified comparison folder based on SSIM. Only processes cells where
    new_board has a value of 1.

    Parameters:
        comparison_folder (str, optional): Path to the folder containing images to compare against.
                                          Defaults to 'teal_tiles'.
        region (tuple, optional): The screen region to capture in (left, top, width, height).
                                  Defaults to EMULATOR_REGION.
        rows (int, optional): Number of rows in the grid. Defaults to 4.
        cols (int, optional): Number of columns in the grid. Defaults to 4.
        delay (int, optional): Delay in seconds before capturing. Defaults to 5.
        threshold (float, optional): SSIM similarity threshold. Defaults to 0.95.
        resize_dim (tuple, optional): Dimensions to resize images for comparison (width, height).
                                      Defaults to (300, 300).
        grayscale (bool, optional): Whether to convert images to grayscale. Defaults to True.
        use_parallel (bool, optional): Whether to use parallel processing for comparisons.
                                       Defaults to False.
        max_workers (int, optional): Number of worker threads for parallel processing.
                                     Defaults to 8.
        enable_logging (bool, optional): Whether to enable logging. Defaults to True.
        new_board (List[List[int]], optional): A 2D list representing the board state.
                                              Cells with value 1 will be processed; others skipped.
                                              Defaults to a 4x4 grid filled with 1s.

    Returns:
        List[List[int]]: Updated board after processing. Cells processed will have matched image IDs,
                         others will retain their original values or be set to -1.
    """
    setup_logging(enable_logging)

    logging.info("Starting the image capture and comparison process.")

    # Capture all cell images (reference images)
    logging.info("Capturing cell images...")
    reference_images = capture_cell_images(
        region=region,
        rows=rows,
        cols=cols,
        delay=delay,
        output_prefix="cell",
        output_suffix="10",
    )

    if not reference_images:
        logging.error("No reference images captured. Exiting.")
        return new_board

    # Determine comparison mode based on new_board
    all_ones = is_board_filled_with_ones(new_board)
    if all_ones:
        logging.info("Board is in initialization state. Comparing against all power-of-two images.")
    else:
        logging.info("Board is in intermediate state. Comparing against '1.png', '2.png', and '4.png'.")

    # Load images from the comparison folder
    logging.info(f"Loading images from comparison folder: '{comparison_folder}'")
    folder_images = load_images_from_folder(
        folder_path=comparison_folder,
        resize_dim=resize_dim,  # Ensure this matches the reference image preprocessing
        grayscale=grayscale
    )

    if not folder_images:
        logging.error(f"No valid images found in the folder '{comparison_folder}'. Exiting.")
        return new_board

    if all_ones:
        # Initialization: Compare against all power-of-two images
        target_filenames = get_all_power_of_two_filenames(folder_images)
        if not target_filenames:
            logging.error("No power-of-two images found in the folder for initialization.")
            return new_board
    else:
        # Intermediate steps: Compare only against '1.png', '2.png', and '4.png'
        target_filenames = ['1.png', '2.png', '4.png']

    # Create a mapping from ID to filename for reference
    id_to_filename = {id: filename for (id, filename, _) in folder_images}

    # Identify cells to process based on new_board
    cells_to_process = []
    cell_indices = []  # To keep track of cell positions

    for row in range(rows):
        for col in range(cols):
            if new_board[row][col] == 1:
                # Calculate the index in reference_images list
                index = row * cols + col
                if index < len(reference_images):
                    cells_to_process.append(reference_images[index])
                    cell_indices.append((row, col))
                else:
                    logging.warning(f"Index {index} out of range for reference_images.")

    if not cells_to_process:
        logging.info("No cells marked for processing. Exiting.")
        return new_board

    # Process reference images: convert to grayscale and resize
    processed_reference_images = []
    for idx, reference_image in enumerate(cells_to_process, start=1):
        # Convert to grayscale if required
        if grayscale:
            try:
                reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
                logging.info(f"Reference Image {idx}: Converted to grayscale.")
            except Exception as e:
                logging.error(f"Error converting reference image {idx} to grayscale: {e}")
                processed_reference_images.append(None)
                continue  # Skip this image

        # Resize the reference image to match folder images
        try:
            reference_image = cv2.resize(reference_image, resize_dim)
            logging.info(f"Reference Image {idx}: Resized to {reference_image.shape}.")
        except Exception as e:
            logging.error(f"Error resizing reference image {idx}: {e}")
            processed_reference_images.append(None)
            continue  # Skip this image

        processed_reference_images.append(reference_image)

    # Filter out any None images resulting from processing errors
    valid_processed_images = [
        img for img in processed_reference_images if img is not None
    ]
    valid_cell_indices = [
        cell_indices[i] for i in range(len(processed_reference_images)) if processed_reference_images[i] is not None
    ]

    if not valid_processed_images:
        logging.error("No valid reference images after processing. Exiting.")
        return new_board

    # Find similar images for the processed reference images
    logging.info("Starting similarity comparisons...")
    similar_image_ids = find_similar_images_for_references(
        reference_images=valid_processed_images,
        folder_images=folder_images,
        threshold=threshold,        # 95% similarity by default
        resize_dim=resize_dim,      # Resize images to 300x300
        grayscale=grayscale,        # Convert images to grayscale
        use_parallel=use_parallel,  # Enable parallel processing if needed
        max_workers=max_workers,    # Adjust based on your CPU cores
        target_filenames=target_filenames  # Pass the target filenames based on board state
    )

    # Update the new_board with the results
    for idx, match_value in enumerate(similar_image_ids):
        row, col = valid_cell_indices[idx]
        if match_value is not None:
            new_board[row][col] = match_value
            logging.info(f"Reference Image ({row}, {col}): Matched with value {match_value}.")
        else:
            new_board[row][col] = -1  # Or retain original value if desired
            logging.info(f"Reference Image ({row}, {col}): No matching image found with similarity >= {threshold*100}%. Set to -1.")

    logging.info("Image capture and comparison process completed.")
    return new_board


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Capture and Comparison Script")
    parser.add_argument('--disable-logging', action='store_true', help="Disable logging output.")
    # Add other arguments as needed to override defaults
    args = parser.parse_args()

    # Initial delay before starting
    time.sleep(5)

    # Initialize the board with all cells marked as 1
    board = [[1 for _ in range(4)] for _ in range(4)]

    # Run the process for a specified number of iterations
    for _ in range(1000):
        board = main(
            enable_logging=not args.disable_logging,
            new_board=board
        )
        print(board)  # Display the updated board
        board = next_board(board)  # Update the board for the next iteration
