# 导出 CSV/Excel文件的接口
# modules/exporter.py
import pandas as pd
import os

from pandas.core.internals import DataManager


class DataExporter(DataManager):
    """
    数据导出类
    """
    def __init__(self, data):
        self.data = data
        os.makedirs('exports', exist_ok=True)

    def export_to_csv(self, filename, folder='exports'):
        """
        导出为 CSV 文件
        """
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        self.data.to_csv(filepath, index=False)
        return filepath

    def export_to_excel(self, filename, folder='exports'):
        """
        导出为 Excel 文件
        """
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        self.data.to_excel(filepath, index=False)
        return filepath