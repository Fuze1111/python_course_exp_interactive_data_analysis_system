# 主程序
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
import pandas as pd
from datetime import datetime
import os
import json

from modules.cleaner import DataCleaning
from modules.uploader import DataUploader
from modules.visualizer import DataVisualizer
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

    # 确定要导出的数据框，优先选择清洗后的数据
    if CLEANED_DF is not None:
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
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    global GLOBAL_DF
    if GLOBAL_DF is None:
        flash("请先上传数据文件")
        return redirect(url_for('index'))

    # 传递必要的变量，避免模板报错
    saved_params = {}
    columns = list(GLOBAL_DF.columns) if GLOBAL_DF is not None else []
    return render_template(
        'analyze.html',
        saved_params=saved_params,
        columns=columns
    )
@app.route('/visualize', methods=['GET'])
def visualize_page():
    global GLOBAL_DF, CLEANED_DF, FILENAME

    # 决定使用哪个 DataFrame 进行可视化
    df_to_visualize = None
    if CLEANED_DF is not None:
        df_to_visualize = CLEANED_DF
    elif GLOBAL_DF is not None:
        df_to_visualize = GLOBAL_DF
    
    if df_to_visualize is None:
        flash("请先上传并处理数据。", "warning")
        return redirect(url_for('index'))

    try:
        visualizer = DataVisualizer(df_to_visualize.copy()) # 使用副本以防意外修改
        all_columns = visualizer.get_available_columns()
        numeric_columns = visualizer.get_numeric_columns()
        categorical_columns = visualizer.get_categorical_columns()
    except Exception as e:
        flash(f"加载可视化页面时出错: {str(e)}", "danger")
        return redirect(url_for('index')) # 或者重定向到上一个有效页面

    return render_template('visualize.html',
                           filename=FILENAME,
                           all_columns=all_columns,
                           numeric_columns=numeric_columns,
                           categorical_columns=categorical_columns)

@app.route('/generate_visualization_plot', methods=['POST'])
def generate_visualization_plot():
    global GLOBAL_DF, CLEANED_DF

    df_to_visualize = None
    if CLEANED_DF is not None:
        df_to_visualize = CLEANED_DF
    elif GLOBAL_DF is not None:
        df_to_visualize = GLOBAL_DF
    
    if df_to_visualize is None:
        return jsonify({"error": "没有可用的数据进行可视化。"}), 400

    try:
        data = request.get_json()
        chart_type = data.get('chart_type')
        params = data.get('params', {})
        
        # 从params中提取通用参数
        title = params.pop('chart_title', None) # chart_title 是通用参数

        visualizer = DataVisualizer(df_to_visualize.copy())
        fig = None

        # 根据 chart_type 调用相应的方法
        if chart_type == 'histogram':
            # 从 params 中获取特定于直方图的参数
            hist_column = params.get('hist_column')
            nbins = params.get('hist_nbins')
            if nbins: nbins = int(nbins) # nbins需要是整数
            hist_color_column = params.get('hist_color_column')
            if not hist_column:
                return jsonify({"error": "直方图需要指定数据列。"}), 400
            fig = visualizer.plot_histogram(column=hist_column, nbins=nbins, color_column=hist_color_column, title=title)
        
        elif chart_type == 'scatter':
            x_col = params.get('scatter_x_column')
            y_col = params.get('scatter_y_column')
            color_col = params.get('scatter_color_column')
            size_col = params.get('scatter_size_column')
            if not x_col or not y_col:
                 return jsonify({"error": "散点图需要指定X轴和Y轴列。"}), 400
            fig = visualizer.plot_scatter(x_column=x_col, y_column=y_col, color_column=color_col, size_column=size_col, title=title)

        elif chart_type == 'line':
            x_col = params.get('line_x_column')
            y_col = params.get('line_y_column') # 注意：DataVisualizer可能支持多y列，前端目前是单选
            color_col = params.get('line_color_column')
            markers = params.get('line_markers', False) # 来自复选框
            if not x_col or not y_col:
                return jsonify({"error": "折线图需要指定X轴和Y轴列。"}), 400
            fig = visualizer.plot_line(x_column=x_col, y_columns=y_col, color_column=color_col, title=title, markers=markers)

        elif chart_type == 'bar':
            x_col = params.get('bar_x_column')
            y_col = params.get('bar_y_column')
            color_col = params.get('bar_color_column')
            orientation = params.get('bar_orientation', 'v')
            barmode = params.get('bar_mode', 'group')
            if not x_col or not y_col:
                return jsonify({"error": "柱状图需要指定X轴和Y轴列。"}), 400
            fig = visualizer.plot_bar(x_column=x_col, y_column=y_col, color_column=color_col, title=title, orientation=orientation, barmode=barmode)

        elif chart_type == 'box':
            y_col = params.get('box_y_column')
            x_col = params.get('box_x_column')
            color_col = params.get('box_color_column')
            notched = params.get('box_notched', False)
            if not y_col:
                return jsonify({"error": "箱线图需要指定Y轴列。"}), 400
            fig = visualizer.plot_box(y_column=y_col, x_column=x_col, color_column=color_col, title=title, notched=notched)

        elif chart_type == 'pie':
            names_col = params.get('pie_names_column')
            values_col = params.get('pie_values_column')
            hole_str = params.get('pie_hole')
            hole = float(hole_str) if hole_str else 0.0 # 转换为浮点数
            if not names_col or not values_col:
                 return jsonify({"error": "饼图需要指定标签列和数值列。"}), 400
            fig = visualizer.plot_pie(names_column=names_col, values_column=values_col, title=title, hole=hole)

        elif chart_type == 'heatmap':
            # heatmap_columns 是一个列表，如果为空则使用所有数值列
            selected_cols = params.get('heatmap_columns')
            if selected_cols and not isinstance(selected_cols, list): # 如果前端只传了一个，但应该是列表
                selected_cols = [selected_cols]
            # 如果 selected_cols 是空列表或 None，DataVisualizer.plot_correlation_heatmap会处理
            fig = visualizer.plot_correlation_heatmap(numeric_cols=selected_cols if selected_cols else None, title=title)
        
        else:
            return jsonify({"error": f"不支持的图表类型: {chart_type}"}), 400

        if fig:
            # 将 Plotly figure 转换为 JSON spec (不包含 JavaScript)
            # Plotly.js 在前端会使用这个 spec 来渲染图表
            plot_spec_json = fig.to_json() # 这是Plotly推荐的在前后端分离时传递图表的方式
            return jsonify({"plot_spec": plot_spec_json})
        else:
            return jsonify({"error": "未能生成图表对象。"}), 500

    except ValueError as ve: #捕获DataVisualizer内部可能抛出的列名错误等
        return jsonify({"error": f"参数错误: {str(ve)}"}), 400
    except Exception as e:
        app.logger.error(f"生成图表时出错: {e}", exc_info=True) # 记录详细错误到服务器日志
        return jsonify({"error": f"生成图表时发生内部错误: {str(e)}"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
