"""
From raw dataset 
"""

import pandas as pd
import yaml 

class DataCleaner: 
    def __init__(self, config):
        self.config = config

    def remove_irrelevant(self, input_df: pd.DataFrame):
        pass
        
    def handle_missing_values(self, input_df: pd.DataFrame):
        pass

    def clean_data(self, input_df: pd.DataFrame):
        print("Cleaning dataset...")
        print(f"Original dataset size: {input_df.shape}")
        self.remove_irrelevant(input_df)


if __name__ == "__main__":
    cleaner = DataCleaner()