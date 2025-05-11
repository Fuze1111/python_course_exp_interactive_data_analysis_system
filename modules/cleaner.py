#缺失值处理 & 异常值检测
import pandas as pd
import numpy as np
from scipy.stats import zscore


class DataCleaning:
    def __init__(self, data):
        self.data = data

    def handle_missing_values(self, method='drop', fill_value=None):
        """
        Handles missing values in the dataset.

        Args:
            method: Method to handle missing values ('drop', 'fill').
            fill_value: Value to fill missing values with (only used if method is 'fill').
        """
        if method == 'drop':
            self.data.dropna()
        elif method == 'fill' and fill_value is not None:
            self.data.fillna(fill_value)
        else:
            raise ValueError("Invalid method or fill_value not provided for 'fill' method.")
        return self.data

    def detect_outliers(self, column, threshold=3):
        """
        Detects outliers in a specified column using Z-score method.

        Args:
            column: Column name to check for outliers.
            threshold: Z-score threshold for outlier detection.
        """
        if column not in self.data.columns:
            raise ValueError(f"Column '{column}' not found in the data.")
        self.data['z_score'] = zscore(self.data[column])
        outliers = self.data[np.abs(self.data['z_score']) > threshold]
        self.data = self.data.drop(columns=['z_score'])
        return outliers
