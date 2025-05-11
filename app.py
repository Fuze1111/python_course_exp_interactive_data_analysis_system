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
    # 渲染前10行为 HTML 表格
    # 在app.py中修改表格生成代码
    table_html = df.head(10).to_html(
        classes='table table-striped table-bordered table-responsive',
        index=False,
        border=0,
        justify='left'
    )
    return render_template('index.html', table_html=table_html)




if __name__ == '__main__':
    app.run(debug=True)
