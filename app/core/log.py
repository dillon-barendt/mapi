"""
TODO: Add structlog for row progression and error handling
"""

import logging

from structlog import get_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)
