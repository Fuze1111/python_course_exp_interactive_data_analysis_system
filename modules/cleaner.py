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
            self.data = self.data.dropna()
        elif method == 'fill' and fill_value is not None:
            self.data = self.data.fillna(fill_value)
        else:
            raise ValueError("Invalid method or fill_value not provided for 'fill' method.")
        return self.data

    def detect_outliers(self, column, threshold=3, replacement=None):
        """
        Detects outliers in a specified column using Z-score method.

        Args:
            column: Column name to check for outliers.
            threshold: Z-score threshold for outlier detection.
        """
        if column not in self.data.columns:
            raise ValueError(f"列 '{column}' 不存在。")

        # 确保列中没有缺失值并且是数值类型
        self.data.loc[:, column] = pd.to_numeric(self.data[column], errors='coerce')
        self.data = self.data.dropna(subset=[column])

        self.data['z_score'] = zscore(self.data[column])
        if replacement is not None:
            # 替换异常值
            self.data.loc[np.abs(self.data['z_score']) > threshold, column] = replacement
        else:
            # 删除异常值
            self.data = self.data[np.abs(self.data['z_score']) <= threshold]
        self.data = self.data.drop(columns=['z_score'])
        return self.data

    def handle_duplicates(self, method='drop'):
        """
        处理重复值
        """
        if method == 'drop':
            self.data = self.data.drop_duplicates()
        elif method == 'mark':
            self.data['is_duplicate'] = self.data.duplicated()
        else:
            raise ValueError("无效的重复值处理方法。")
        return self.data

    def apply_cleaning_rules(self, rules):
        """
        应用自动化清洗规则
        Args:
            rules: 清洗规则（字典格式）
                示例：
                {
                    "missing_values": {"method": "fill", "fill_value": 0},
                    "outliers": {"column": "age", "threshold": 3}
                    "duplicates": {"method": "drop"},
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
            replacement = outlier_rules.get('replacement')
            self.detect_outliers(column, threshold,replacement)
        #处理重复值
        if 'duplicates' in rules:
            dup_rules = rules['duplicates']
            self.handle_duplicates(method=dup_rules.get('method', 'drop'))
        self.data.reset_index(drop=True, inplace=True)
        return self.data
