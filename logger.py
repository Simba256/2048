# logger.py

import logging
import argparse

def setup_logging(enable_logging: bool):
    """
    Sets up logging with separate log files for each module.
    
    Parameters:
        enable_logging (bool): Whether to enable logging.
    """
    # Obtain the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

    if not enable_logging:
        logging.disable(logging.CRITICAL)
        return

    # Define log format
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    # Handler for main.log (main.py)
    main_handler = logging.FileHandler('main.log')
    main_handler.setLevel(logging.INFO)
    main_handler.setFormatter(formatter)
    main_handler.addFilter(lambda record: record.name == '__main__')

    # Handler for image_similarity.log (image_similarity.py)
    image_similarity_handler = logging.FileHandler('image_similarity.log')
    image_similarity_handler.setLevel(logging.DEBUG)
    image_similarity_handler.setFormatter(formatter)
    image_similarity_handler.addFilter(lambda record: record.name.startswith('image_similarity'))

    # Handler for cell_images.log (cell_images.py)
    cell_images_handler = logging.FileHandler('cell_images.log')
    cell_images_handler.setLevel(logging.DEBUG)
    cell_images_handler.setFormatter(formatter)
    cell_images_handler.addFilter(lambda record: record.name.startswith('cell_images'))

    # Add handlers to the root logger
    logger.addHandler(main_handler)
    logger.addHandler(image_similarity_handler)
    logger.addHandler(cell_images_handler)