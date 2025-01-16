# cell_images.py

import pyautogui
import cv2
import numpy as np
import time
import logging
from typing import Tuple, List

# Obtain a module-level logger
logger = logging.getLogger(__name__)

# 1. Configuration
# ----------------------------------------------------
# The regions of the screen where different applications are located.
# This is (left, top, width, height) in pixels.
EMULATOR_REGION = (688, 299, 494, 495)  # emulator
WHATSAPP_REGION = (798, 354, 328, 328)  # whatsapp

def capture_board(region: Tuple[int, int, int, int] = EMULATOR_REGION) -> np.ndarray:
    """
    Captures the specified screen region and returns a BGR image (NumPy array).

    Parameters:
        region (tuple): The region to capture in (left, top, width, height) format.

    Returns:
        np.ndarray: The captured image in BGR format.
    """
    logger.info(f"Capturing screen region: {region}")
    # Capture using PyAutoGUI (PIL format)
    screenshot = pyautogui.screenshot(region=region)
    
    # Convert PIL (RGB) to NumPy (RGB)
    frame = np.array(screenshot)
    
    # Convert RGB to BGR for OpenCV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    logger.debug(f"Captured image shape: {frame.shape}")
    return frame

def get_cell_image(board_img: np.ndarray, row: int, col: int, rows: int, cols: int) -> np.ndarray:
    """
    Extracts the sub-image corresponding to (row, col) in a grid.

    Parameters:
        board_img (np.ndarray): The full board screenshot (BGR).
        row (int): The row index (0-based).
        col (int): The column index (0-based).
        rows (int): Total number of rows in the grid.
        cols (int): Total number of columns in the grid.

    Returns:
        np.ndarray: The cropped cell image.
    """
    height, width, _ = board_img.shape
    
    # Each cell's width and height
    cell_width = width // cols
    cell_height = height // rows
    
    # Calculate the bounding box for this cell
    x1 = col * cell_width
    y1 = row * cell_height
    x2 = x1 + cell_width
    y2 = y1 + cell_height
    
    # Crop the cell from the board image
    cell_img = board_img[y1:y2, x1:x2]
    logger.debug(f"Cropped cell ({row}, {col}) shape: {cell_img.shape}")
    return cell_img

def capture_cell_images(
    region: Tuple[int, int, int, int] = EMULATOR_REGION,
    rows: int = 4,
    cols: int = 4,
    delay: int = 5,
    output_prefix: str = "cell",
    output_suffix: str = "10",
) -> List[np.ndarray]:
    """
    Captures the screen region, divides it into a grid of cells, saves each cell as an image,
    and returns the list of cell images.

    Parameters:
        region (tuple, optional): The screen region to capture in (left, top, width, height).
                                   Defaults to EMULATOR_REGION.
        rows (int, optional): Number of rows in the grid. Defaults to 4.
        cols (int, optional): Number of columns in the grid. Defaults to 4.
        delay (int, optional): Delay in seconds before capturing. Defaults to 5.
        output_prefix (str, optional): Prefix for saved cell image filenames. Defaults to "cell".
        output_suffix (str, optional): Suffix for saved cell image filenames. Defaults to "10".

    Returns:
        List[np.ndarray]: List of cropped cell images.
    """
    logger.info(f"Starting capture in {delay} seconds...")
    time.sleep(delay)
    
    # 1. Capture the whole board region
    board_img = capture_board(region)
    logger.info("Captured the entire board region.")
    
    cell_images = []
    # 2. Divide into grid cells and save each cell image
    for row in range(rows):
        for col in range(cols):
            cell_img = get_cell_image(board_img, row, col, rows, cols)
            cell_images.append(cell_img)
            filename = f"{output_prefix}_{row}_{col}_{output_suffix}.png"
            try:
                cv2.imwrite(filename, cell_img)
                logger.info(f"Saved {filename}")
            except Exception as e:
                logger.error(f"Failed to save {filename}: {e}")
    
    logger.info("Completed capturing all cell images.")
    return cell_images

if __name__ == "__main__":
    capture_cell_images()
