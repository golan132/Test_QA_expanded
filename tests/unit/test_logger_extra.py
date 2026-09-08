from src.utils.logger import TestLogger

TestLogger.__test__ = False


def test_logger_error_debug():
    logger = TestLogger("test")
    # This just ensures we call the wrappers and hit lines 46 and 49
    logger.error("error message")
    logger.debug("debug message")
