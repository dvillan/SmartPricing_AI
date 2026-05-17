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
        self.dataset = Dataset("data/Estudios_Economicos_Consolidado.xlsx", config)

    def data_cleaning(self): 
        print("Performing data cleaning phase...")
        self.dataset.clean_dataset()

    def data_transformation(self):
        print("Performing data transformations...")
        self.dataset.transform_dataset()

    def train(self):
        print("Executing training phase...")

    def evaluate(self):
        print("Evaluating created models...")

    def execute(self):
        print("Executing pipeline")
        self.data_cleaning()
        self.data_transformation()
        self.train()
        self.evaluate()

        self.teardown()

    def teardown(self):
        if args.phase == 'all': 
            print("Pipeline executed successfully")
        else: 
            print("Phase completed")


if __name__ == "__main__":

    # CLI creation 
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--phase', type=str, help='Phase of the pipeline to be implemented',
                        default='all')
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
