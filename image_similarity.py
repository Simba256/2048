# image_similarity.py

import cv2
import os
from skimage.metrics import structural_similarity as ssim
import numpy as np
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Obtain a module-level logger
logger = logging.getLogger(__name__)

def load_images_from_folder(
    folder_path: str,
    resize_dim: Tuple[int, int] = (300, 300),
    grayscale: bool = True
) -> List[Tuple[int, str, Optional[np.ndarray]]]:
    """
    Loads all images from the specified folder, assigns a unique integer ID to each image,
    and returns a list of tuples containing (ID, filename, image).

    Parameters:
        folder_path (str): Path to the folder containing images.
        resize_dim (tuple, optional): Dimensions to resize images (width, height). Defaults to (300, 300).
        grayscale (bool, optional): Whether to convert images to grayscale. Defaults to True.

    Returns:
        List[Tuple[int, str, Optional[np.ndarray]]]: 
            A list where each tuple contains:
                - ID (int): Unique integer identifier for the image.
                - filename (str): Name of the image file.
                - image (Optional[np.ndarray]): The processed OpenCV image. None if loading fails.
    """
    image_list = []
    supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')

    if not os.path.isdir(folder_path):
        logger.error(f"The folder path '{folder_path}' does not exist or is not a directory.")
        return image_list

    for idx, filename in enumerate(os.listdir(folder_path), start=1):
        if not filename.lower().endswith(supported_extensions):
            logger.warning(f"Skipping unsupported file type: {filename}")
            continue

        image_path = os.path.join(folder_path, filename)
        image = cv2.imread(image_path)

        if image is None:
            logger.warning(f"Unable to load image: {image_path}. Skipping.")
            image_list.append((idx, filename, None))
            continue

        # Handle images with alpha channels (e.g., PNGs with transparency)
        if len(image.shape) == 3 and image.shape[2] == 4:
            try:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
                logger.debug(f"Converted image '{filename}' from BGRA to BGR.")
            except Exception as e:
                logger.error(f"Error converting image '{filename}' from BGRA to BGR: {e}. Skipping.")
                image_list.append((idx, filename, None))
                continue

        # Convert to grayscale if required
        if grayscale:
            try:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                logger.debug(f"Converted image '{filename}' to grayscale.")
            except Exception as e:
                logger.error(f"Error converting image '{filename}' to grayscale: {e}. Skipping.")
                image_list.append((idx, filename, None))
                continue

        # Resize the image
        try:
            image = cv2.resize(image, resize_dim)
            logger.debug(f"Resized image '{filename}' to {image.shape}.")
        except Exception as e:
            logger.error(f"Error resizing image '{filename}': {e}. Skipping.")
            image_list.append((idx, filename, None))
            continue

        # Verify the shape after preprocessing
        expected_shape = (resize_dim[1], resize_dim[0]) if grayscale else (resize_dim[1], resize_dim[0], 3)
        if image.shape != expected_shape:
            logger.error(f"Image '{filename}' has incorrect shape {image.shape}. Expected {expected_shape}. Skipping.")
            image_list.append((idx, filename, None))
            continue

        # Debug: Print image shape after preprocessing
        logger.debug(f"Loaded and preprocessed image '{filename}' with shape {image.shape}.")

        image_list.append((idx, filename, image))

    logger.info(f"Loaded {len(image_list)} images from folder '{folder_path}'.")
    return image_list

def find_similar_images_for_references(
    reference_images: List[np.ndarray],
    folder_images: List[Tuple[int, str, Optional[np.ndarray]]],
    threshold: float = 0.95,
    resize_dim: Tuple[int, int] = (300, 300),
    grayscale: bool = True,
    use_parallel: bool = False,
    max_workers: int = 4,
    target_filenames: Optional[List[str]] = None  # New parameter
) -> List[Optional[int]]:
    """
    For each reference image, compares it against specified target images in the folder,
    computes SSIM scores, and returns 1, 2, 4, ..., based on the highest similarity
    if it meets the threshold. Returns None if no SSIM score meets the threshold.

    Parameters:
        reference_images (List[np.ndarray]): List of reference OpenCV images to compare.
        folder_images (List[Tuple[int, str, Optional[np.ndarray]]]): 
            List of tuples containing (ID, filename, image) from the folder.
        threshold (float, optional): SSIM similarity threshold (default is 0.95).
        resize_dim (tuple, optional): Dimensions to resize images for comparison (width, height).
                                      Defaults to (300, 300).
        grayscale (bool, optional): Whether the images are already in grayscale.
                                    Defaults to True.
        use_parallel (bool, optional): Whether to use parallel processing.
                                       Defaults to False.
        max_workers (int, optional): Number of worker threads for parallel processing.
                                     Defaults to 4.
        target_filenames (Optional[List[str]], optional): 
            List of specific filenames to compare against. If None, compares against all images.
            Defaults to None.

    Returns:
        List[Optional[int]]: 
            A list where each element corresponds to a reference image and contains:
                - The integer value corresponding to the best matching image (e.g., 1, 2, 4, ..., 16384).
                - None if no matching image meets the threshold.
    """
    similar_image_ids = []

    # Define mapping from filenames to their integer values
    filename_to_value = {}
    if target_filenames is not None:
        for fname in target_filenames:
            basename = os.path.splitext(fname.lower())[0]
            if basename.isdigit():
                filename_to_value[fname.lower()] = int(basename)
            else:
                logger.warning(f"Filename '{fname}' does not represent an integer value.")
    else:
        # If target_filenames is None, consider all images in the folder
        for (id, filename, image) in folder_images:
            basename = os.path.splitext(filename.lower())[0]
            if basename.isdigit():
                filename_to_value[filename.lower()] = int(basename)
            else:
                logger.warning(f"Filename '{filename}' does not represent an integer value.")

    # Filter folder_images based on target_filenames if provided
    if target_filenames is not None:
        processed_folder_images = [
            (id, filename, image) 
            for (id, filename, image) in folder_images 
            if filename.lower() in [fname.lower() for fname in target_filenames] and image is not None
        ]
    else:
        processed_folder_images = [
            (id, filename, image) 
            for (id, filename, image) in folder_images 
            if image is not None
        ]

    if not processed_folder_images:
        logger.error("No target images found in the folder to compare.")
        return [None] * len(reference_images)

    def compare_reference_to_targets(ref_img: np.ndarray) -> Optional[int]:
        """
        Compare a single reference image against the target images and return the
        value corresponding to the best match if it meets the threshold.

        Parameters:
            ref_img (np.ndarray): The reference image.

        Returns:
            Optional[int]: The integer value of the best matching image, or None if no match meets the threshold.
        """
        best_score = -1  # Initialize with a score lower than the minimum possible SSIM
        best_value = None

        for (folder_id, filename, folder_img) in processed_folder_images:
            # Ensure both images have the same dimensions
            if ref_img.shape != folder_img.shape:
                logger.warning(f"Image '{filename}' has shape {folder_img.shape}, which does not match the reference image shape {ref_img.shape}. Skipping.")
                continue

            # Compute SSIM
            try:
                score, _ = ssim(ref_img, folder_img, full=True)
                logger.debug(f"SSIM between reference image and '{filename}': {score:.4f}")
            except Exception as e:
                logger.error(f"Error computing SSIM for folder image '{filename}': {e}. Skipping.")
                continue

            # Update best score and value if current score is higher
            if score > best_score:
                best_score = score
                best_value = filename_to_value.get(filename.lower())

        # Check if the best score meets the threshold
        if best_score >= threshold:
            logger.info(f"Reference image matched with '{filename}' (Value: {best_value}) with SSIM score: {best_score:.4f}")
            return best_value
        else:
            logger.info(f"No matching image found for reference image with SSIM >= {threshold:.2f}. Best SSIM: {best_score:.4f}")
            return None

    if use_parallel:
        logger.info("Using parallel processing for image comparisons.")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit a separate task for each reference image
            futures = [executor.submit(compare_reference_to_targets, ref_img) for ref_img in reference_images]

            for future in as_completed(futures):
                result = future.result()
                similar_image_ids.append(result)
    else:
        logger.info("Using sequential processing for image comparisons.")
        for ref_idx, ref_image in enumerate(reference_images, start=1):
            logger.debug(f"Processing Reference Image {ref_idx} with shape: {ref_image.shape}")
            match_value = compare_reference_to_targets(ref_image)
            similar_image_ids.append(match_value)

    logger.info("Completed similarity comparisons.")
    return similar_image_ids
