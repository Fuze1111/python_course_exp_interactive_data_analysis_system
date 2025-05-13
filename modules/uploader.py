# 上传 & 格式检查
# modules/uploader.py
import os
import pandas as pd
from werkzeug.utils import secure_filename
from modules.data_management import DataManagement

class DataUploader(DataManagement):
    def __init__(self, data_path=None):
        super().__init__(data_path)

    def allowed_file(self, filename):
        """判断文件扩展名是否在允许列表中."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def save_and_load(self, file_storage, upload_folder):
        """
        保存上传文件并返回 DataFrame。
        file_storage: Flask 中 request.files['datafile']
        upload_folder: app.config['UPLOAD_FOLDER']
        """
        filename = secure_filename(file_storage.filename)
        if not self.allowed_file(filename):
            raise ValueError("支持 CSV、XLS、XLSX 文件")

        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file_storage.save(filepath)

        # 更新当前实例的数据路径
        self.data_path = filepath

        # 加载数据到DataFrame
        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'csv':
            self.data = pd.read_csv(filepath)
        else:
            self.data = pd.read_excel(filepath)

        return self.data