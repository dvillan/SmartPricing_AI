"""
Dataset manager script, all changes to the dataset will happen here
"""

import pandas as pd
import yaml

from data_transformer import DataTransformer
from data_cleaner import DataCleaner

class Dataset:
    def __init__(self, filepath, config, logger):
        self.filepath = filepath
        self.raw_data = pd.read_excel(filepath, sheet_name=None)
        self.config = config
        self.logger = logger

    def clean_dataset(self):
        cleaner = DataCleaner(self.config, self.logger)
        cleaner.clean_data(self.raw_data)

    def transform_dataset(self):
        transformer = DataTransformer()
    
    def save_dataset(self):
        pass

if __name__ == "__main__":
    dataset = Dataset("data/Estudios_Economicos_Consolidado.xlsx")