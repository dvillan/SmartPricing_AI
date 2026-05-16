"""
Main script for project pipeline execution
"""

import argparse
import pandas as pd 
import os

from dataset import Dataset
from model import Model

class Pipeline: 
    def __init__(self, args):
        self.args = args
        self.dataset = Dataset("data/Estudios_Economicos_Consolidado.xlsx")

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

    pipeline = Pipeline(args)
    pipeline.execute()
