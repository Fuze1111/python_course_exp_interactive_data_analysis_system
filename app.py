# 主程序
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
import pandas as pd
from datetime import datetime
import io
import base64
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
import json

from narwhals.selectors import categorical

from modules import DataCleaning, DataUploader, DataVisualizer, DataExporter, DataAnalyzer

# 全局 DataFrame 存储
GLOBAL_DF = None
# 新增全局变量存储文件名
FILENAME = None
# 新增全局变量存储清洗后的数据
CLEANED_DF = None

# 解决matplotlib中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

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
    global GLOBAL_DF, CLEANED_DF

    # 优先使用清洗后的数据
    df_to_analyze = CLEANED_DF if CLEANED_DF is not None else GLOBAL_DF

    if df_to_analyze is None:
        flash("请先上传数据文件")
        return redirect(url_for('index'))

    # 尝试将可能是数值的字符串列转换为数值类型
    df_converted = df_to_analyze.copy()
    for column in df_converted.columns:
        if df_converted[column].dtype == 'object':  # 如果是对象类型（可能是字符串）
            try:
                # 尝试转换为数值
                df_converted[column] = pd.to_numeric(df_converted[column], errors='coerce')
                # 如果转换成功（没有太多NaN），保留转换结果
                if df_converted[column].isna().sum() <= len(df_converted) * 0.1:  # 允许10%的NaN
                    df_to_analyze[column] = df_converted[column]
            except:
                pass  # 无法转换则保持原样

    saved_params = {}
    columns = list(df_to_analyze.columns)
    # 更新数值列列表
    numeric_columns = list(df_to_analyze.select_dtypes(include=['number']).columns)
    # 更新分类列列表
    categorical_columns = list(df_to_analyze.select_dtypes(exclude=['number']).columns)
    ml_results = None
    ml_metrics = None
    feature_importance_chart = None
    predictions_chart = None
    cluster_chart = None

    if request.method == 'POST':
        form = request.form
        saved_params = form.to_dict(flat=False)
        # 处理多选特征
        features = form.getlist('features')
        target_column = form.get('target_column')
        ml_algorithm = form.get('ml_algorithm')
        test_size = float(form.get('test_size') or 20) / 100

        # 先转换所选特征和目标列为数值型
        df_for_ml = df_to_analyze.copy()
        converted_features = []
        for feature in features:
            if feature not in numeric_columns:
                try:
                    df_for_ml[feature] = pd.to_numeric(df_for_ml[feature], errors='coerce')
                    df_for_ml[feature] = df_for_ml[feature].fillna(df_for_ml[feature].mean())
                    converted_features.append(feature)
                except Exception as e:
                    flash(f"特征 '{feature}' 无法转换为数值: {str(e)}", "warning")
                    # 继续处理其他特征

        if target_column and target_column not in numeric_columns and ml_algorithm in ['linear_regression', 'random_forest_regression']:
            try:
                df_for_ml[target_column] = pd.to_numeric(df_for_ml[target_column], errors='coerce')
                df_for_ml[target_column] = df_for_ml[target_column].fillna(df_for_ml[target_column].mean())
            except Exception as e:
                flash(f"目标列 '{target_column}' 无法转换为数值: {str(e)}", "danger")
                return render_template(
                    'analyze.html',
                    saved_params=saved_params,
                    columns=columns,
                    numeric_columns=numeric_columns,
                    ml_results=ml_results,
                    ml_metrics=ml_metrics,
                    feature_importance_chart=feature_importance_chart,
                    predictions_chart=predictions_chart,
                    cluster_chart=cluster_chart
                )

        # 查找转换后有大量缺失值的特征
        problematic_features = []
        for feature in features:
            if df_for_ml[feature].isna().sum() > len(df_for_ml) * 0.2:  # 超过20%的值缺失
                problematic_features.append(feature)

        if problematic_features:
            flash(f"以下特征转换为数值后有大量缺失值: {', '.join(problematic_features)}", "warning")

        if converted_features:
            flash(f"以下特征已自动转换为数值: {', '.join(converted_features)}", "info")

        analyzer = DataAnalyzer(df_for_ml)

        try:
            if ml_algorithm == 'linear_regression':
                result = analyzer.predict(features, target_column, test_size=test_size, method='linear')
                ml_metrics = {'MSE': result['mse'], 'R2': result['r2']}

                # 生成预测结果图
                plt.figure(figsize=(10, 6))
                plt.scatter(result['y_test'], result['y_pred'], alpha=0.5)
                plt.plot([min(result['y_test']), max(result['y_test'])],
                         [min(result['y_test']), max(result['y_test'])], 'r--')
                plt.xlabel('实际值')
                plt.ylabel('预测值')
                plt.title('线性回归: 预测值 vs 实际值')

                # 将图保存到内存中
                img_buf = io.BytesIO()
                plt.savefig(img_buf, format='png')
                img_buf.seek(0)
                predictions_chart = "data:image/png;base64," + base64.b64encode(img_buf.read()).decode('utf-8')
                plt.close()

            elif ml_algorithm == 'random_forest_regression':
                result = analyzer.predict(features, target_column, test_size=test_size, method='random_forest')
                ml_metrics = {'MSE': result['mse'], 'R2': result['r2']}

                # 生成特征重要性图
                if result['feature_importance']:
                    # 排序特征重要性
                    importance_df = pd.DataFrame({
                        '特征': list(result['feature_importance'].keys()),
                        '重要性': list(result['feature_importance'].values())
                    })
                    importance_df = importance_df.sort_values('重要性', ascending=False)

                    plt.figure(figsize=(10, 6))
                    sns.barplot(x='重要性', y='特征', data=importance_df)
                    plt.title('随机森林回归: 特征重要性')
                    plt.tight_layout()

                    img_buf = io.BytesIO()
                    plt.savefig(img_buf, format='png')
                    img_buf.seek(0)
                    feature_importance_chart = "data:image/png;base64," + base64.b64encode(img_buf.read()).decode(
                        'utf-8')
                    plt.close()

                # 生成预测结果图
                plt.figure(figsize=(10, 6))
                plt.scatter(result['y_test'], result['y_pred'], alpha=0.5)
                plt.plot([min(result['y_test']), max(result['y_test'])],
                         [min(result['y_test']), max(result['y_test'])], 'r--')
                plt.xlabel('实际值')
                plt.ylabel('预测值')
                plt.title('随机森林回归: 预测值 vs 实际值')

                img_buf = io.BytesIO()
                plt.savefig(img_buf, format='png')
                img_buf.seek(0)
                predictions_chart = "data:image/png;base64," + base64.b64encode(img_buf.read()).decode('utf-8')
                plt.close()

            elif ml_algorithm == 'random_forest_classification':
                result = analyzer.classify(features, target_column, test_size=test_size)
                ml_metrics = {'准确率': result['accuracy']}

                # 生成特征重要性图
                if result['feature_importance']:
                    # 排序特征重要性
                    importance_df = pd.DataFrame({
                        '特征': list(result['feature_importance'].keys()),
                        '重要性': list(result['feature_importance'].values())
                    })
                    importance_df = importance_df.sort_values('重要性', ascending=False)

                    plt.figure(figsize=(10, 6))
                    sns.barplot(x='重要性', y='特征', data=importance_df)
                    plt.title('随机森林分类: 特征重要性')
                    plt.tight_layout()

                    img_buf = io.BytesIO()
                    plt.savefig(img_buf, format='png')
                    img_buf.seek(0)
                    feature_importance_chart = "data:image/png;base64," + base64.b64encode(img_buf.read()).decode(
                        'utf-8')
                    plt.close()

            elif ml_algorithm == 'kmeans':
                n_clusters = int(form.get('n_clusters') or 3)
                result = analyzer.cluster_kmeans(features, n_clusters=n_clusters)
                ml_metrics = {'轮廓系数': result['silhouette_score']}

                # 生成聚类可视化图
                if len(features) >= 2:
                    # 若特征数大于2，则使用前两个特征进行可视化
                    plt.figure(figsize=(10, 6))
                    scatter = plt.scatter(
                        df_for_ml[features[0]],
                        df_for_ml[features[1]],
                        c=result['data']['cluster'],
                        cmap='viridis',
                        alpha=0.6
                    )
                    plt.scatter(
                        result['cluster_centers'][:, 0],
                        result['cluster_centers'][:, 1],
                        c='red',
                        marker='x',
                        s=100
                    )
                    plt.xlabel(features[0])
                    plt.ylabel(features[1])
                    plt.title(f'K均值聚类结果 (k={n_clusters})')
                    plt.colorbar(scatter, label='聚类')

                    img_buf = io.BytesIO()
                    plt.savefig(img_buf, format='png')
                    img_buf.seek(0)
                    cluster_chart = "data:image/png;base64," + base64.b64encode(img_buf.read()).decode('utf-8')
                    plt.close()

            elif ml_algorithm == 'dbscan':
                eps = float(form.get('eps') or 0.5)
                min_samples = int(form.get('min_samples') or 5)
                result = analyzer.cluster_dbscan(features, eps=eps, min_samples=min_samples)
                ml_metrics = {'轮廓系数': result['silhouette_score'] or 0}

                # 生成聚类可视化图
                if len(features) >= 2:
                    # 若特征数大于2，则使用前两个特征进行可视化
                    plt.figure(figsize=(10, 6))
                    scatter = plt.scatter(
                        df_for_ml[features[0]],
                        df_for_ml[features[1]],
                        c=result['data']['cluster'],
                        cmap='viridis',
                        alpha=0.6
                    )
                    plt.xlabel(features[0])
                    plt.ylabel(features[1])
                    plt.title(f'DBSCAN聚类结果 (eps={eps}, min_samples={min_samples})')
                    plt.colorbar(scatter, label='聚类 (-1表示噪声点)')

                    img_buf = io.BytesIO()
                    plt.savefig(img_buf, format='png')
                    img_buf.seek(0)
                    cluster_chart = "data:image/png;base64," + base64.b64encode(img_buf.read()).decode('utf-8')
                    plt.close()

            elif ml_algorithm == 'pca':
                n_components = int(form.get('n_components') or 2)
                result = analyzer.dimensionality_reduction(features, n_components=n_components)
                ml_metrics = {'累计方差解释率': result['explained_variance']['cumulative_variance_ratio'][-1]}

                # 生成PCA可视化图
                if n_components >= 2:
                    # 创建PCA结果散点图
                    plt.figure(figsize=(12, 10))
                    plt.subplot(2, 1, 1)
                    plt.scatter(
                        result['reduced_data']['PC1'],
                        result['reduced_data']['PC2'],
                        alpha=0.7
                    )
                    plt.xlabel('主成分1')
                    plt.ylabel('主成分2')
                    plt.title('PCA降维结果散点图')

                    # 创建解释方差比例条形图
                    plt.subplot(2, 1, 2)
                    plt.bar(
                        range(len(result['explained_variance']['explained_variance_ratio'])),
                        result['explained_variance']['explained_variance_ratio']
                    )
                    plt.plot(
                        range(len(result['explained_variance']['cumulative_variance_ratio'])),
                        result['explained_variance']['cumulative_variance_ratio'],
                        'r-o'
                    )
                    plt.xlabel('主成分')
                    plt.ylabel('解释方差比例')
                    plt.title('PCA解释方差比例')
                    plt.xticks(range(len(result['explained_variance']['components'])),
                               result['explained_variance']['components'])
                    plt.tight_layout()

                    img_buf = io.BytesIO()
                    plt.savefig(img_buf, format='png')
                    img_buf.seek(0)
                    cluster_chart = "data:image/png;base64," + base64.b64encode(img_buf.read()).decode('utf-8')
                    plt.close()

            else:
                flash("请选择有效的算法")
                return redirect(url_for('analyze'))

            ml_results = True  # 标记有结果

        except Exception as e:
            flash(f"分析失败: {str(e)}", "danger")

    return render_template(
        'analyze.html',
        saved_params=saved_params,
        columns=columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        ml_results=ml_results,
        ml_metrics=ml_metrics,
        feature_importance_chart=feature_importance_chart if 'feature_importance_chart' in locals() else None,
        predictions_chart=predictions_chart if 'predictions_chart' in locals() else None,
        cluster_chart=cluster_chart if 'cluster_chart' in locals() else None
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
