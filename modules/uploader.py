# 上传 & 格式检查
# modules/uploader.py
import os
import pandas as pd
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

def allowed_file(filename):
    """判断文件扩展名是否在允许列表中."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_and_load(file_storage, upload_folder):
    """
    保存上传文件并返回 DataFrame。
    file_storage: Flask 中 request.files['datafile']
    upload_folder: app.config['UPLOAD_FOLDER']
    """
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        raise ValueError("只支持 CSV、XLS、XLSX 文件")
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file_storage.save(filepath)

    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'csv':
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
    return df
