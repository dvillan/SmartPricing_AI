import argparse
import pandas as pd 
import os 

class Pipeline: 
    def __init__(self, args):
        self.args = args

    def data_cleaning(self): 
        print("Performing data cleaning...")

    def data_transformation(self):
        print("Performing data transformations...")

    def train(self):
        print("Executing training phase...")

    def evaluate(self):
        print("Evaluating created models...")

    def execute(self):
        print("Executing pipeline")
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
