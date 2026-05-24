"""
Main script for project pipeline execution
"""

import argparse
import pandas as pd
import utils 
import os

from dataset import Dataset
from model import Model

class Pipeline: 
    def __init__(self, phase, logger, config):
        self.phase = phase
        self.logger = logger
        self.config = config
        self.dataset = Dataset("data/Estudios_Economicos_Consolidado.xlsx", config, logger)

    def execute(self):

        # Phases definition
        if self.phase == "clean":
            self.dataset.clean_dataset()
        elif self.phase == "transform":
            self.dataset.transform_dataset()
        elif self.phase == "train": 
            pass 
        elif self.phase == "evaluate":
            pass
        else:
            # Perform all phases from pipeline
            self.logger.info("Executing pipeline...")
            self.dataset.clean_dataset()
            self.dataset.transform_dataset()

        self.teardown()

    def teardown(self):
        if self.phase == 'all': 
            self.logger.info("Pipeline executed successfully")
        else: 
            self.logger.info("Phase completed")


if __name__ == "__main__":

    # CLI creation 
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--phase', type=str, help='Phase of the pipeline to be implemented',
                        default='all', choices=["all", "clean", "transform", "train", "evaluate"])
    args = parser.parse_args()
    phase = args.phase

    if os.path.exists("/logs"):
        print("Creating log folder...")
        os.mkdir("/logs")

    config = utils.get_config()
    logger = utils.create_logger(config)
    logger.info("Initializing SmartPricing AI")

    pipeline = Pipeline(phase, logger, config)
    pipeline.execute()
