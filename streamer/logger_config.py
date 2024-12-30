import logging

def setup_logging():
    logging.basicConfig(
        level=logging.NOTSET,  # Set the logging level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the format
        handlers=[
            logging.StreamHandler(),  # Log to console
            logging.FileHandler('streamer_debug.log')
        ]
    )
