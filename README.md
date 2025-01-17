
# 2048 Game Automation Tool

This repository contains a Python-based automation tool for the popular game 2048. The tool attempts to read the game board state and automatically send swipe commands (Up, Down, Left, Right, Undo) to progress through the game. Several approaches to tile detection are included, but the final solution uses **SSIM** comparison against a labeled dataset of tile images (e.g., `2.png`, `4.png`, `8.png`, etc.).

---

## Features

- **Multiple tile-detection attempts**:
  - **YOLOv11** with a custom dataset
  - **Tesseract OCR**
  - **SSIM** (final approach) with labeled tile images
- **Configurable key mappings** for sending swipe and undo commands
- **Screenshots** for each cell (e.g., `cell_0_0_10.png`, `cell_3_3_10.png`) for debugging
- Adjustable board dimensions (default is **4×4**)
- Adjustable total moves to be made by the engine (default is **1000**)

---

## Requirements

- **Python 3.12** (or a compatible version)
- [Bluestacks Emulator](https://www.bluestacks.com/) (or another Android emulator)
- Install dependencies via:
  ```bash
  pip install -r requirements.txt
  ```

---

## Installation

1. **Clone** this repository:
   ```bash
   git clone https://github.com/Simba256/2048.git
   cd 2048-automation
   ```
2. **Install** required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up** the Bluestacks (or your preferred emulator) window in fullscreen mode if you plan to use the included default coordinates. Otherwise, update the relevant constants in code (see **Configuration**).

---

## Usage

1. **Start** your Bluestacks emulator and open the 2048 game.
2. **Configure** key mappings inside Bluestacks to match the tool’s expected keys:
   - `Up` → **Arrow up**
   - `Down` → **Arrow down**
   - `Left` → **Arrow left**
   - `Right` → **Arrow right**
   - `Undo` → **u**  

   These can be changed in [`game.py`](game.py), in the `key_map` dictionary:
   ```python
   key_map = {
       'up':    'up',
       'down':  'down',
       'left':  'left',
       'right': 'right',
       'undo':  'u'
   }
   ```
3. **Run** the script:
   ```bash
   python main.py
   ```
4. The bot will attempt up to 1000 moves by default and automatically take screenshots to identify tile values.

---

## Configuration

1. **Emulator Window Dimensions**  
   In [`game.py`](game.py) (or anywhere else coordinates are defined), ensure that the **EMULATOR** window dimensions match your system. By default, these dimensions are tuned for **Bluestacks** in fullscreen.

2. **Saving Screenshots**  
   Screenshots of each cell (e.g., `cell_0_0_10.png` to `cell_3_3_10.png`) are saved by default. If you **do not** want to save them:
   - **Comment out** line 112 in [`cell_images.py`](cell_images.py):
     ```python
     # cv2.imwrite(filename, cell_img)
     ```

3. **Grid Size (Default 4×4)**  
   If your 2048 variant uses a grid larger or smaller than 4×4, update the grid size in [`main.py`](main.py).  
   Around line **246** (where `board = main(...)` is called), pass `rows` and `cols` to the `main` function:
   ```python
   board = main(
       enable_logging=not args.disable_logging,
       new_board=board,
       rows=4,
       cols=4
   )
   ```
   Adjust `rows` and `cols` to match your version of the game.

4. **Number of Moves**  
   By default, the script runs for **1000** moves. To change this, modify the **for** loop around line **245** in [`main.py`](main.py):
   ```python
   for _ in range(1000):
       ...
   ```
   Set it to any number you prefer.

---

## How It Works

1. **Capture Board State**  
   The script takes a screenshot of each cell in the 4×4 grid (or your custom dimensions) by parsing specific coordinates corresponding to the emulator window.

2. **Tile Detection**  
   Instead of using YOLOv11 or Tesseract (which had varying degrees of accuracy), the final approach uses **SSIM** (Structural Similarity) to compare each captured cell against a folder of labeled tile images (`1.png` for empty, `2.png`, `4.png`, `8.png`, and so on).

3. **Deciding the Move (Strategy)**  
   - **Chain of Tiles:** The strategy aims to arrange tiles in a decreasing order starting from the bottom-right corner. The largest tile should be at the bottom-right, the next largest to its left (or adjacent), and so on.
   - **Heuristic Scoring:**  
     1. **Encourage Larger Tiles:** For every tile on the board, the script adds `pow(3, log2(tile))` to a running score. This rewards creating bigger tiles, since a tile like `32` contributes more than `2` or `16`.  
     2. **Prioritize the Chain:** In addition, for any tile that is in the correct position to maintain the decreasing chain from the bottom-right corner, it adds `pow(4, log2(tile))`. Using base 4 here further emphasizes the importance of tiles placed in descending order.  

   This combined scoring heuristic guides the engine to produce larger tiles and keep them aligned in a decreasing sequence along the bottom row and rightmost column, thus maximizing the chance of reaching (and surpassing!) 2048.

4. **Repeat**  
   The process repeats for a defined number of moves or until the game terminates.

---

## Contributing

Feel free to submit issues or pull requests to improve the code, enhance detection, or add more sophisticated game strategies.

---

## License

This project is provided under the [MIT License](LICENSE). You are free to fork, modify, and use it for your own 2048 automation endeavors.

**Happy automating, and may you finally reach that coveted 262144 tile (or beyond)!**
