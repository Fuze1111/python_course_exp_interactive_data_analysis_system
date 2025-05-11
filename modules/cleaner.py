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

    def apply_cleaning_rules(self, rules):
        """
        应用自动化清洗规则
        Args:
            rules: 清洗规则（字典格式）
                示例：
                {
                    "missing_values": {"method": "fill", "fill_value": 0},
                    "outliers": {"column": "age", "threshold": 3}
                }
        Returns:
            清洗后的 DataFrame
        """
        if 'missing_values' in rules:
            mv_rules = rules['missing_values']
            self.handle_missing_values(method=mv_rules.get('method', 'drop'),
                                       fill_value=mv_rules.get('fill_value'))
        if 'outliers' in rules:
            outlier_rules = rules['outliers']
            column = outlier_rules.get('column')
            threshold = outlier_rules.get('threshold', 3)
            self.detect_outliers(column, threshold)
        return self.data