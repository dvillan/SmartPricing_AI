"""
From raw dataset 
"""

import pandas as pd
import yaml
import unicodedata
import numpy as np
import os
import re

pd.set_option('future.no_silent_downcasting', True)

class DataCleaner: 
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.num_variables = self.config["data_processing"]["relevant_variables"]["num"]
        self.cat_variables = self.config["data_processing"]["relevant_variables"]["cat"]
        self.state_map = self.config["mapeo_estado"]
        self.category_map = self.config["mapeo_categoria"]

    ###############################
    # Auxiliary functions
    ###############################

    def normalize_text(self, text):
        """
        Return input text all on caps, collapse spaces and return NaN if empty
        """
        if pd.isna(text):
            return text
        text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')
        text = text.upper().strip()
        text_norm = re.sub(r'\s+', ' ', text)

        return text_norm if text_norm else np.nan
    
    def clean_text(self, df):
        """
        Sets correct object data type
        """
        df = df.copy()
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['', 'nan', 'NaN', 'None', 'NaT'], np.nan)
        
        return df 

    def cast_numeric(self, df, input_list):
        """
        Sets correct numeric data type for given input list
        """
        for col in input_list: 
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    
    ###############################
    # Main functions
    ###############################

    def run_resumen_flow(self, df):
        df = df.copy()
        
        # Set correct data types 
        res_df_clean = self.clean_text(df)
        res_df_clean_v1 = self.cast_numeric(res_df_clean, self.num_variables)

        # Normalize categoric columns, remove accents and set caps
        for col in self.cat_variables:
            res_df_clean_v1[col] = res_df_clean_v1[col].apply(self.normalize_text)

        # Map 'estado' column to avoid duplicates
        res_df_clean_v1['estado'] = res_df_clean_v1['estado'].map(lambda x: self.state_map.get(x, x))

        return res_df_clean_v1

    def run_detalle_flow(self, df): 
        df = df.copy()

        # Set correct data types 
        det_df_clean = self.clean_text(df)

        # Normalize categoric columns, remove accents and set caps
        det_df_clean['categoria'] = det_df_clean['categoria'].apply(self.normalize_text)
        det_df_clean['tipo_servicio'] = det_df_clean['tipo_servicio'].apply(self.normalize_text)

        # Map 'categoria' column to avoid duplicates
        det_df_clean['categoria'] = det_df_clean['categoria'].map(lambda x: self.category_map.get(x, x))

        return det_df_clean

    def clean_data(self, input_df):
        """
        """
        self.logger.info("Cleaning dataset...")

        # Define dataset sheet names 
        resumen_sheetname = self.config["dataset_sheets"]["resumen"]
        detalle_sheetname = self.config["dataset_sheets"]["detalle"]

        # Get dataframes by sheet 
        resumen_df = input_df[resumen_sheetname]
        detalle_df = input_df[detalle_sheetname]

        # Initial dataset size 
        for name, df in input_df.items():
            self.logger.info(f"Original {name} size: {df.shape}")

        # Perform cleaning steps 
        resumen_df_clean = self.run_resumen_flow(resumen_df)
        detalle_df_clean = self.run_detalle_flow(detalle_df)

        # Size after cleaning 
        self.logger.info(f"{resumen_sheetname} size after data cleaning: {resumen_df_clean.shape}")
        self.logger.info(f"{detalle_sheetname} size after data cleaning: {detalle_df_clean.shape}")

        # Save cleaned dataframe
        cleaned_data_name = os.path.join(self.config['filepaths']['clean_dataset'], "dataset_cleaned.xlsx")
        with pd.ExcelWriter(cleaned_data_name, engine='openpyxl') as writer:
            resumen_df_clean.to_excel(writer, sheet_name=resumen_sheetname, index=False)
            detalle_df_clean.to_excel(writer, sheet_name=detalle_sheetname, index=False)


