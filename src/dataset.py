"""
Dataset manager script, all changes to the dataset will happen here
"""

import pandas as pd

from data_transformer import DataTransformer
from data_cleaner import DataCleaner

class Dataset:
    def __init__(self, filepath):
        self.filepath = filepath
        self.raw_data = pd.read_excel(filepath)

    def clean_dataset(self):
        cleaner = DataCleaner()

    def transform_dataset(self):
        transformer = DataTransformer()

if __name__ == "__main__":
    dataset = Dataset("data/Estudios_Economicos_Consolidado.xlsx")