"""
Auxiliary functions for the project 
"""

import yaml 
from datetime import datetime
import logging
import logging.config

def get_config():
    with open("src/config.yaml", "r") as config: 
        config = yaml.safe_load(config)

    return config

def create_logger(config):
    log_filename = f"logs/log_{datetime.now().strftime('%Y-%m-%d__%H-%M-%S')}.log"
    logger = logging.getLogger("ML_log")
    config['logger']['handlers']['file']['filename'] = log_filename
    logging.config.dictConfig(config=config['logger'])
    
    return logger


if __name__ == '__main__':

    config = get_config()
    logger = create_logger(config)
    # logger.debug("debug_message")
    # logger.info("info_message")