"""
Apply appropriate data transformations for the specified dataset
"""

import pandas as pd
import numpy as np
import os 

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    PowerTransformer, KBinsDiscretizer, OneHotEncoder, LabelEncoder
)
from sklearn.feature_selection import (
    VarianceThreshold, f_regression, mutual_info_regression,
    chi2, SelectKBest
)

###############################
# Helper classes 
###############################

class FeatureCreator:

    def resumen_create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Create "safe" features to avoid divisions by cero
        df["_empleados_safe"] = df["total_empleados"].replace(0, np.nan)
        df['_costo_safe'] = df['total_costo_servicio'].replace(0, np.nan)
        df['_mano_obra_safe'] = df['total_mano_obra_anual'].replace(0, np.nan)
        df['_facturacion_safe'] = df['facturacion_anual'].replace(0, np.nan)

        # Operative intensity features 
        df['mano_obra_por_empleado'] = df['total_mano_obra_anual'] / df['_empleados_safe']
        df['materiales_por_empleado'] = df['materiales_anual'] / df['_empleados_safe']
        df['maquinaria_por_empleado'] = df['equipo_maquinaria'] / df['_empleados_safe']

        # Cost composition features 
        df['ratio_mano_obra'] = df['total_mano_obra_anual'] / df['_costo_safe']
        df['ratio_materiales'] = df['materiales_anual'] / df['_costo_safe']
        df['ratio_maquinaria'] = df['equipo_maquinaria'] / df['_costo_safe']
        df['ratio_subcontratos'] = df['subcontratos_anual'] / df['_costo_safe']
        df['ratio_cargas_sociales']= df['carga_social_anual'] / df['_costo_safe']
        df['ratio_prestaciones'] = df['prestaciones_anual'] / df['_costo_safe']

        # Binning 
        emp_series = df['total_empleados'].fillna(0).values.reshape(-1,1)
        kbins = KBinsDiscretizer(n_bins=4, encode='ordinal', strategy='quantile')
        df['segmento_tamano'] = kbins.fit_transform(emp_series).astype(int)

        labels_tamano = {0: 'Pequeño', 1: 'Mediano', 2: 'Grande', 3: 'Muy grande'}
        df['segmento_tamano_lbl'] = df['segmento_tamano'].map(labels_tamano)

        return df

    def detalle_create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Aggregtions
        detalle_agg = df.groupby('archivo').agg(
            n_categorias_laborales = ('categoria', 'nunique'),
            n_partidas_plantilla = ('categoria', 'size'),
            importe_anual_mediano = ('importe_anual', 'median'),
            importe_anual_std = ('importe_anual', 'std'),
            empleados_max_categoria= ('num_empleados', 'max'),
            ).reset_index()
        
        detalle_agg['cv_importe_categoria'] = (
            detalle_agg['importe_anual_std'] / detalle_agg['importe_anual_mediano'].replace(0, np.nan))
        
        return detalle_agg


class EncodingHandler:
    def __init__(self, config):
        self.config = config

    def cat_group(self, col, min_freq=3, label='OTROS'):
        # Group uncommon categories 
        cnt = col.value_counts(dropna=False)
        group = cnt[cnt < min_freq].index
        
        return col.where(~col.isin(group), label)
    
    def create_groupings(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Manage missing values (Median imputation)
        for c in ['n_categorias_laborales', 'n_partidas_plantilla',
          'importe_anual_mediano', 'importe_anual_std',
          'empleados_max_categoria', 'cv_importe_categoria']:
            df[c] = df[c].fillna(df[c].median())

        # Group uncommon categories and manage missing values if any
        cat_to_group = self.config["data_processing"]["cat_groupings"]
        for col in cat_to_group: 
            if col in df.columns:
                df[col] = df[col].fillna('DESCONOCIDO').astype(str).str.strip()
                df[col] = self.cat_group(df[col], min_freq=3)

        return df

    def freq_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Manage high cardinality variables
        for col in ['cliente', 'centro']:
            if col in df.columns:
                freq_map = df[col].value_counts(normalize=True).to_dict()
                df[f'{col}_freq'] = df[col].map(freq_map)
        
        return df 
    
    def ord_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        orden_tamano = {'Pequeño': 0, 'Mediano': 1, 'Grande': 2, 'Muy grande': 3}
        df['segmento_tamano_ord'] = df['segmento_tamano_lbl'].map(orden_tamano)

        return df 
    
    def bin_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df['condiciones_pago_bin'] = (
            df['condiciones_pago'].astype(str).str.contains('90', na=False).astype(int))

        return df
    
    def one_hot_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cat_onehot = ['tipo_servicio', 'region', 'plaza', 'estado']
        df_fe_encoded = pd.get_dummies(df, columns=cat_onehot, drop_first=True, dtype=int)

        return df_fe_encoded
    
    def encode_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df_v1 = self.create_groupings(df)
        df_v2 = self.freq_encoding(df_v1)
        df_v3 = self.ord_encoding(df_v2)
        df_v4 = self.bin_encoding(df_v3)
        df_encoded = self.one_hot_encoding(df_v4)

        return df_encoded


class SkewHandler:
    def __init__(self, config):
        self.config = config

    def transform_comparison(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Initialize transformers 
        pt_yeo = PowerTransformer(method='yeo-johnson', standardize=False)
        pt_bc = PowerTransformer(method='box-cox', standardize=False)

        comparativo = []
        for v in self.config["data_processing"]["skew_candidates"]:
            x = df[v].astype(float).copy()
            # log1p: clip a >=0 por seguridad (estas variables son no-negativas por naturaleza)
            x_clip = x.clip(lower=0)
            x_log = np.log1p(x_clip)

            # Yeo-Johnson (acepta cualquier valor)
            x_yeo = pt_yeo.fit_transform(x.values.reshape(-1, 1)).ravel()

            # Box-Cox sólo si todos los valores son estrictamente positivos
            if (x > 0).all():
                x_bc = pt_bc.fit_transform(x.values.reshape(-1, 1)).ravel()
                skew_bc = pd.Series(x_bc).skew()
            else:
                skew_bc = np.nan

            comparativo.append({
                'variable': v,
                'skew_original': x.skew(),
                'skew_log1p': pd.Series(x_log).skew(),
                'skew_yeo': pd.Series(x_yeo).skew(),
                'skew_boxcox': skew_bc,
            })

            comp_df = pd.DataFrame(comparativo).set_index('variable').round(3)

        return comp_df

    def apply_skew_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Make skew comparison
        comparison_df = self.transform_comparison(df)

        # Refit transformers 
        pt_yeo = PowerTransformer(method='yeo-johnson', standardize=False)
        pt_bc = PowerTransformer(method='box-cox', standardize=False)

        for v in self.config["data_processing"]["skew_candidates"]:
            skews = comparison_df.loc[v, ['skew_log1p', 'skew_yeo', 'skew_boxcox']].abs()
            mejor = skews.idxmin()
            # Choose log1p if difference is <0.3
            if mejor != 'skew_log1p' and not pd.isna(skews['skew_log1p']):
                if (skews['skew_log1p'] - skews[mejor]) < 0.30:
                    mejor = 'skew_log1p'

            x = df[v].astype(float).values
            if mejor == 'skew_log1p':
                df[f'{v}_trans'] = np.log1p(np.clip(x, 0, None))
            elif mejor == 'skew_yeo':
                df[f'{v}_trans'] = pt_yeo.fit_transform(x.reshape(-1, 1)).ravel()
            else:
                df[f'{v}_trans'] = pt_bc.fit_transform(x.reshape(-1, 1)).ravel()

        return df
    

class ScalingHandler: 
    def __init__(self, config):
        self.config = config
        self.var_to_trans = self.config["data_processing"]["skew_candidates"]
        self.col_trans = [f'{v}_trans' for v in self.var_to_trans]
        self.cols_no_trans_numericas = [
            'ratio_mano_obra', 'ratio_materiales', 'ratio_maquinaria',
            'ratio_subcontratos', 'ratio_cargas_sociales', 'ratio_prestaciones',
            'segmento_tamano_ord', 'cliente_freq', 'centro_freq',
            'n_categorias_laborales', 'n_partidas_plantilla', 'cv_importe_categoria']
    
    def scale_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        df_scaled = df.copy()

        # Manage missing values if any 
        imp = SimpleImputer(strategy='median')
        df_scaled[self.col_trans + self.cols_no_trans_numericas] = imp.fit_transform(
            df_scaled[self.col_trans + self.cols_no_trans_numericas])
        
        # Robust scaler for economic variables and standard for the rest
        scaler_robust = RobustScaler()
        scaler_std = StandardScaler()

        df_scaled[self.col_trans] = scaler_robust.fit_transform(df_scaled[self.col_trans])
        df_scaled[self.cols_no_trans_numericas] = scaler_std.fit_transform(
            df_scaled[self.cols_no_trans_numericas])
        
        return df_scaled


###############################
# Main class
###############################

class DataTransformer:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.feature_creator = FeatureCreator()
        self.encoding_handler = EncodingHandler(config=self.config)
        self.skew_handler = SkewHandler(config=self.config)
        self.scaling_handler = ScalingHandler(config=self.config)

    ###############################
    # Auxiliary functions
    ###############################

    def is_binary(self, series): 
        vals = pd.Series(series).dropna().unique()
        return len(vals) <= 2 and set(vals).issubset({0, 1, 0.0, 1.0})
    
    def filter_vars(self, df: pd.DataFrame) -> pd.DataFrame:
        self.y = df['facturacion_anual_trans']

        # Exclude original variables, keep transformations
        exclude = {
        'facturacion_anual_trans', 'facturacion_anual',
        'facturacion_mensual', 'archivo', 'archivo_nombre', 'rfc',
        'contacto', 'telefono', 'numero_concurso', 'referencia',
        'cliente', 'centro', 'segmento_tamano_lbl', 'condiciones_pago',
        'fecha_entrega', 'fecha_analisis', 'vigencia_inicio', 'vigencia_fin',
        'validez_oferta', 'nombre_proyecto', 'elaboro', 'cargo_elaboro',
        'codigo_ubicacion', 'codigo_region', 'poblacion', 'domicilio', 'cp',
        'resumen_cliente', 'resumen_centro', 'resumen_fecha', 'resumen_servicio',
        'edo_cliente', 'edo_centro', 'edo_fecha', 'edo_proyecto', 'edo_servicio',
        '_empleados_safe', '_costo_safe', '_mano_obra_safe', '_facturacion_safe',
        'categoria_facturacion', 'anio_analisis', 'segmento_tamano'}

        exclude |= {f'{v}' for v in self.config['data_processing']['skew_candidates'] if v != 'facturacion_anual'}

        candidates = [
            c for c in df.select_dtypes(include=[np.number]).columns
            if c not in exclude and not c.startswith('ee_')
        ]

        # Remove columns with variance=0
        X = df[candidates].copy()
        X = X.loc[:, X.notna().any() & (X.nunique() > 1)]

        # Security imputation
        X = X.fillna(X.median(numeric_only=True))

        # Manage original variables 
        cols_bin = [c for c in X.columns if self.is_binary(X[c])]
        cols_cont = [c for c in X.columns if c not in cols_bin]

        scaler_final_candidatas = RobustScaler()
        if cols_cont:
            X[cols_cont] = scaler_final_candidatas.fit_transform(X[cols_cont])

        return X

    ###############################
    # Main functions
    ###############################

    def transform_resumen(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        res_df = self.feature_creator.resumen_create_features(df)
        return res_df

    def transform_detalle(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        det_df = self.feature_creator.detalle_create_features(df)
        return det_df
    
    def apply_transformations(self, input_df: pd.DataFrame):
        """
        """
        self.logger.info("Applying required transformations to the dataset...")

        # Define dataset sheet names 
        resumen_sheetname = self.config["dataset_sheets"]["resumen"]
        detalle_sheetname = self.config["dataset_sheets"]["detalle"]

        # Get dataframes by sheet 
        resumen_df = input_df[resumen_sheetname]
        detalle_df = input_df[detalle_sheetname]

        # Initial dataset size 
        for name, df in input_df.items():
            self.logger.info(f"Clean {name} size: {df.shape}")

        # Apply transformation steps 
        detalle_df_transf = self.transform_detalle(detalle_df)
        resumen_df_transf = self.transform_resumen(resumen_df)

        # Merge individual dataframes
        trans_df = resumen_df_transf.merge(detalle_df_transf, on='archivo', how='left')

        # Apply encodings 
        encoded_df = self.encoding_handler.encode_dataset(trans_df)

        # Manage skew by applying transformations
        deskewed_df = self.skew_handler.apply_skew_transformations(encoded_df)

        # Manage different scale on variables by applying Scalings 
        scaled_df = self.scaling_handler.scale_variables(deskewed_df)

        # Filter non-relevant variables 
        final_df = self.filter_vars(scaled_df)

        self.logger.debug("Transformations applied")


        # Size after tranformations
        # self.logger.info(f"{resumen_sheetname} size after data transformations: {resumen_df_transf.shape}")
        # self.logger.info(f"{detalle_sheetname} size after data transformations: {detalle_df_transf.shape}")

        # Save cleaned dataframe
        final_df_name = self.config['filepaths']['final_dataset']
        final_df.to_csv(final_df_name, index=False)
