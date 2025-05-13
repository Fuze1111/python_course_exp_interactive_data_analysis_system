#主程序
from flask import Flask, render_template, request, flash, redirect, url_for

from modules.cleaner import DataCleaning
from modules.uploader import DataUploader
import pandas as pd

# 全局 DataFrame 存储
GLOBAL_DF = None
# 新增全局变量存储文件名
FILENAME = None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'key'  # 用于 flash 消息


@app.route('/', methods=['GET'])
def index():
    # 首页展示上传表单或预览
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    global GLOBAL_DF, FILENAME
    f = request.files.get('datafile')
    if not f or f.filename == '':
        flash("未选择文件，请重新上传")
        return redirect(url_for('index'))


    try:
        uploader = DataUploader()
        df = uploader.save_and_load(f, app.config['UPLOAD_FOLDER'])
        # 获取文件名
        FILENAME = f.filename
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))

    # 存储到全局以供后续清洗使用
    GLOBAL_DF = df

    # 直接重定向到清洗界面，不再显示预览页面
    return redirect(url_for('clean'))

@app.route('/clean', methods=['GET', 'POST'])
def clean():
    global GLOBAL_DF

    if GLOBAL_DF is None:
        flash("请先上传数据文件")
        return redirect(url_for('index'))

    if request.method == 'POST':
        #获取清洗规则
        missing_method = request.form.get('missing_method')
        fill_value = request.form.get('fill_value')
        outlier_column = request.form.get('outlier_column')
        threshold = request.form.get('threshold', type=float)
        replacement = request.form.get('replacement')
        duplicate_method = request.form.get('duplicate_method')

        # 构建清洗规则
        rules = {
            "missing_values": {"method": missing_method, "fill_value": fill_value} if missing_method == 'fill' else {
                "method": missing_method},
            "outliers": {"column": outlier_column, "threshold": threshold,
                         "replacement": replacement} if outlier_column else None,
            "duplicates": {"method": duplicate_method}
        }

        #清洗数据
        cleaner = DataCleaning(GLOBAL_DF)
        try:
            cleaned_data = cleaner.apply_cleaning_rules(rules)
            cleaned_data = cleaned_data.reset_index(drop=True)
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('clean'))

        # 渲染清洗后的数据
        return render_template(
            'clean.html',
            data=GLOBAL_DF.head(10).to_dict(orient='records'),  # 确保是字典列表
            columns=GLOBAL_DF.columns,
            numeric_columns=GLOBAL_DF.select_dtypes(include=['number']).columns,
            cleaned_data=cleaned_data.head(10).to_dict(orient='records'),  # 确保是字典列表
            cleaned_columns=cleaned_data.columns,
            data_count=len(GLOBAL_DF),
            column_count=len(GLOBAL_DF.columns),
            cleaned_count=len(cleaned_data),
            cleaned_columns_count=len(cleaned_data.columns)
        )

        # GET 请求时渲染清洗页面
    return render_template(
        'clean.html',
        data=GLOBAL_DF.head(10).to_dict(orient='records'),
        columns=GLOBAL_DF.columns,
        numeric_columns=GLOBAL_DF.select_dtypes(include=['number']).columns,
        data_count=len(GLOBAL_DF),
        column_count=len(GLOBAL_DF.columns),
        filename = FILENAME
    )



if __name__ == '__main__':
    app.run(debug=True)
