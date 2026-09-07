import logging
import os
from datetime import datetime

class TestLogger:
    def __init__(self, test_name: str):
        self._test_name = test_name
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger with custom format and file writing
        """
        # Create log directory
        log_dir = "results/logs"
        os.makedirs(log_dir, exist_ok=True)

        # Set file name with timestamp and test name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{log_dir}/{timestamp}_{self._test_name}.log"

        # Setup logger
        logger = logging.getLogger(f"test_{self._test_name}")
        logger.setLevel(logging.DEBUG)
        
        # Add file handler
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Add stream handler to preserve console output
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(stream_handler)

        return logger

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def warning(self, message: str):
        self.logger.warning(message) 