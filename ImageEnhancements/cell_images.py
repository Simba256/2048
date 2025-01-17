import pyautogui
import cv2
import numpy as np
import time

# 1. Configuration
# ----------------------------------------------------
# The region of the screen where the 2048 board is located.
# This is (left, top, width, height) in pixels.
BOARD_REGION = (688, 299, 494, 495)  # emulator
# BOARD_REGION = (798, 354, 328, 328)  # whatsapp

# Dimensions of the board
ROWS = 4
COLS = 4

def capture_board(region=BOARD_REGION):
    """
    Captures the specified screen region and returns a BGR image (NumPy array).
    """
    # Capture using PyAutoGUI (PIL format)
    screenshot = pyautogui.screenshot(region=region)
    
    # Convert PIL (RGB) to NumPy (RGB)
    frame = np.array(screenshot)
    
    # Convert RGB to BGR for OpenCV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

def get_cell_image(board_img, row, col):
    """
    Extract the sub-image corresponding to (row, col) in a 4x4 grid.
    board_img is the full board screenshot (BGR).
    """
    height, width, _ = board_img.shape
    
    # Each cell's width and height
    cell_width = width // COLS
    cell_height = height // ROWS
    
    # Calculate the bounding box for this cell
    x1 = col * cell_width
    y1 = row * cell_height
    x2 = x1 + cell_width
    y2 = y1 + cell_height
    
    # Crop the cell from the board image
    cell_img = board_img[y1:y2, x1:x2]
    return cell_img

def main():

    # time.sleep(5)

    # 1. Capture the whole board region
    board_img = capture_board()
    cv2.imwrite("board10.png", board_img)

    # # 2. Divide into 4x4 cells and save each cell image
    for row in range(ROWS):
        for col in range(COLS):
            cell_img = get_cell_image(board_img, row, col)
            filename = f"cell_{row}_{col}_10.png"
            cv2.imwrite(filename, cell_img)
            print(f"Saved {filename}")

if __name__ == "__main__":
    main()
