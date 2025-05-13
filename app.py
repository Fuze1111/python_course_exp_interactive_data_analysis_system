#主程序
from flask import Flask, render_template, request, flash, redirect, url_for

from modules.cleaner import DataCleaning
from modules.uploader import DataUploader
import pandas as pd

from flask import send_from_directory
from datetime import datetime
import os
from modules.exporter import DataExporter

# 全局 DataFrame 存储
GLOBAL_DF = None
# 新增全局变量存储文件名
FILENAME = None
# 新增全局变量存储清洗后的数据
CLEANED_DF = None

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
    global GLOBAL_DF,CLEANED_DF

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
        if replacement == "":
            replacement = None
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

            # 存储清洗后的数据到全局变量
            CLEANED_DF = cleaned_data
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('clean'))

        # 渲染清洗后的数据
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
            cleaned_columns_count=len(cleaned_data.columns),
            filename=FILENAME
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


# 添加导出数据的路由
@app.route('/export', methods=['GET', 'POST'])
def export_data():
    global GLOBAL_DF, CLEANED_DF

    # 确定要导出的数据框
    source = request.args.get('source')
    if source == 'cleaned' and CLEANED_DF is not None:
        df_to_export = CLEANED_DF
        default_filename = f"cleaned_data_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    elif GLOBAL_DF is not None:
        df_to_export = GLOBAL_DF
        default_filename = f"data_export_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    else:
        flash("请先上传并处理数据文件")
        return redirect(url_for('index'))

    if request.method == 'POST':
        # 获取表单数据
        filename = request.form.get('filename', default_filename)
        export_format = request.form.get('format', 'csv')

        # 确保文件名有正确的扩展名
        if export_format == 'csv' and not filename.endswith('.csv'):
            filename += '.csv'
        elif export_format == 'excel' and not filename.endswith('.xlsx'):
            filename += '.xlsx'

        # 调用 DataExporter 进行导出
        exporter = DataExporter(df_to_export)
        try:
            if export_format == 'csv':
                filepath = exporter.export_to_csv(filename)
            elif export_format == 'excel':
                filepath = exporter.export_to_excel(filename)
            else:
                flash('不支持的导出格式', 'warning')
                # 生成新的时间戳
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                return render_template('result.html',
                                      export_success=False,
                                      timestamp=timestamp)

            # 导出成功，返回结果页面
            return render_template('result.html',
                                   export_success=True,
                                   filepath=filepath,
                                   download_filename=filename,
                                   timestamp=datetime.now().strftime("%Y%m%d%H%M%S"))
        except Exception as e:
            flash(f'导出失败: {str(e)}', 'danger')
            # 生成新的时间戳
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return render_template('result.html',
                                  export_success=False,
                                  timestamp=timestamp)

    # GET 请求时渲染导出页面
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return render_template('result.html',
                          export_success=False,
                          timestamp=timestamp)

# 添加下载文件的路由
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('exports', filename, as_attachment=True)


# 添加分析页面路由
@app.route('/analyze')
def analyze():
    global GLOBAL_DF
    if GLOBAL_DF is None:
        flash("请先上传数据文件")
        return redirect(url_for('index'))

    return render_template('analyze.html')

if __name__ == '__main__':
    app.run(debug=True)
