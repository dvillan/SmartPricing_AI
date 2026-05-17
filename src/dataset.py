"""
Dataset manager script, all changes to the dataset will happen here
"""

import pandas as pd
import yaml

from data_transformer import DataTransformer
from data_cleaner import DataCleaner

class Dataset:
    def __init__(self, filepath, config):
        self.filepath = filepath
        self.raw_data = pd.read_excel(filepath)
        self.config = config

    def clean_dataset(self):
        cleaner = DataCleaner(self.config)

    def transform_dataset(self):
        transformer = DataTransformer()
    
    def save_dataset(self):
        pass

if __name__ == "__main__":
    dataset = Dataset("data/Estudios_Economicos_Consolidado.xlsx")