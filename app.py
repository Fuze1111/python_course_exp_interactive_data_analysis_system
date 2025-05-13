#主程序
from flask import Flask, render_template, request, flash, redirect, url_for
from modules.uploader import save_and_load
import pandas as pd

# 全局 DataFrame 存储
GLOBAL_DF = None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'key'  # 用于 flash 消息


@app.route('/', methods=['GET'])
def index():
    # 首页展示上传表单或预览
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    global GLOBAL_DF
    f = request.files.get('datafile')
    if not f or f.filename == '':
        flash("未选择文件，请重新上传")
        return redirect(url_for('index'))

    try:
        df = save_and_load(f, app.config['UPLOAD_FOLDER'])
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))

    # 存储到全局以供后续清洗使用
    GLOBAL_DF = df

    # 直接重定向到清洗界面，不再显示预览页面
    return redirect(url_for('clean'))

@app.route('/clean', methods=['GET'])
def clean():
    global GLOBAL_DF

    if GLOBAL_DF is None:
        flash("请先上传数据文件")
        return redirect(url_for('index'))

    # 获取数据基本信息
    data_count = len(GLOBAL_DF)
    column_count = len(GLOBAL_DF.columns)
    columns = GLOBAL_DF.columns.tolist()

    # 获取数值型列，用于异常值检测
    numeric_columns = GLOBAL_DF.select_dtypes(include=['number']).columns.tolist()

    return render_template(
        'cleaner.html',
        data=GLOBAL_DF.head(10),  # 只显示前10行
        data_count=data_count,
        column_count=column_count,
        columns=columns,
        numeric_columns=numeric_columns
    )


if __name__ == '__main__':
    app.run(debug=True)
