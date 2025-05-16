import pandas as pd
import plotly.express as px


class DataVisualizer:
    """数据可视化类，用于生成各种图表"""

    def __init__(self, df):
        """初始化数据可视化器"""
        self.df = df

    def get_available_columns(self):
        """获取所有可用列名"""
        return list(self.df.columns)

    def get_numeric_columns(self):
        """获取所有数值类型列"""
        return list(self.df.select_dtypes(include=['number']).columns)

    def get_categorical_columns(self):
        """获取所有分类类型列"""
        return list(self.df.select_dtypes(include=['object', 'category']).columns)

    def plot_histogram(self, column, nbins=None, color_column=None, title=None):
        """
        生成直方图

        参数:
            column: 数据列
            nbins: 分箱数量
            color_column: 颜色分组列
            title: 图表标题
        """
        if column not in self.df.columns:
            raise ValueError(f"列名不存在: {column}")

        if color_column and color_column not in self.df.columns:
            raise ValueError(f"颜色分组列名不存在: {color_column}")

        if nbins is not None:
            try:
                nbins = int(nbins)
            except ValueError:
                raise ValueError("分箱数量必须是整数")

        return px.histogram(
            self.df,
            x=column,
            nbins=nbins,
            color=color_column,
            title=title
        )

    def plot_scatter(self, x_column, y_column, color_column=None, size_column=None, title=None):
        """
        生成散点图

        参数:
            x_column: X轴列
            y_column: Y轴列
            color_column: 颜色分组列
            size_column: 散点大小列
            title: 图表标题
        """
        for col in [x_column, y_column]:
            if col not in self.df.columns:
                raise ValueError(f"列名不存在: {col}")

        for col in [color_column, size_column]:
            if col and col not in self.df.columns:
                raise ValueError(f"列名不存在: {col}")

        return px.scatter(
            self.df,
            x=x_column,
            y=y_column,
            color=color_column,
            size=size_column,
            title=title
        )

    def plot_line(self, x_column, y_columns, color_column=None, title=None, markers=False):
        """
        生成折线图

        参数:
            x_column: X轴列
            y_columns: Y轴列，可以是单个列名或列名列表
            color_column: 颜色分组列
            title: 图表标题
            markers: 是否显示标记点
        """
        if x_column not in self.df.columns:
            raise ValueError(f"X轴列名不存在: {x_column}")

        if isinstance(y_columns, str):
            y_columns = [y_columns]

        for col in y_columns:
            if col not in self.df.columns:
                raise ValueError(f"Y轴列名不存在: {col}")

        if color_column and color_column not in self.df.columns:
            raise ValueError(f"颜色分组列名不存在: {color_column}")

        return px.line(
            self.df,
            x=x_column,
            y=y_columns,
            color=color_column,
            title=title,
            markers=markers
        )

    def plot_bar(self, x_column, y_column, color_column=None, title=None, orientation='v', barmode='group'):
        """
        生成柱状图

        参数:
            x_column: X轴列
            y_column: Y轴列
            color_column: 颜色分组列
            title: 图表标题
            orientation: 方向 ('v' 垂直, 'h' 水平)
            barmode: 多系列时的模式 ('group', 'stack', 'relative')
        """
        for col in [x_column, y_column]:
            if col not in self.df.columns:
                raise ValueError(f"列名不存在: {col}")

        if color_column and color_column not in self.df.columns:
            raise ValueError(f"颜色分组列名不存在: {color_column}")

        if orientation not in ['v', 'h']:
            raise ValueError("方向参数必须是 'v' 或 'h'")

        if barmode not in ['group', 'stack', 'relative']:
            raise ValueError("模式参数必须是 'group', 'stack' 或 'relative'")
        if color_column is not None:
            fig = px.bar(
                self.df,
                x=x_column,
                y=y_column,
                color=color_column,

                title=title,
                orientation=orientation,
                barmode=barmode
            )
        else:
            fig = px.bar(
                self.df,
                x=x_column,
                y=y_column,
                title=title,
                orientation=orientation,
                barmode=barmode,
                color_discrete_sequence=['Red']
            )
        return fig
    def plot_box(self, y_column, x_column=None, color_column=None, title=None, notched=False):
        """
        生成箱线图

        参数:
            y_column: Y轴列
            x_column: X轴分组列
            color_column: 颜色分组列
            title: 图表标题
            notched: 是否显示缺口
        """
        if y_column not in self.df.columns:
            raise ValueError(f"Y轴列名不存在: {y_column}")

        for col in [x_column, color_column]:
            if col and col not in self.df.columns:
                raise ValueError(f"列名不存在: {col}")

        return px.box(
            self.df,
            y=y_column,
            x=x_column,
            color=color_column,
            title=title,
            notched=notched
        )

    def plot_pie(self, names_column, values_column, title=None, hole=0.0):
        """
        生成饼图/环形图

        参数:
            names_column: 标签列
            values_column: 数值列
            title: 图表标题
            hole: 中心孔洞大小 (0-0.99)
        """
        for col in [names_column, values_column]:
            if col not in self.df.columns:
                raise ValueError(f"列名不存在: {col}")

        if not (0.0 <= hole < 1.0):
            raise ValueError("孔洞大小必须在 0.0 到 0.99 之间")

        return px.pie(
            self.df,
            names=names_column,
            values=values_column,
            title=title,
            hole=hole
        )

    def plot_correlation_heatmap(self, numeric_cols=None, title=None):
        """
        生成相关性热力图

        参数:
            numeric_cols: 要包含的数值列列表，默认为所有数值列
            title: 图表标题
        """
        if numeric_cols is None:
            numeric_cols = self.get_numeric_columns()

        if not numeric_cols:
            raise ValueError("没有可用的数值列来生成热力图")

        for col in numeric_cols:
            if col not in self.df.columns:
                raise ValueError(f"列名不存在: {col}")

        # 筛选指定的数值列并计算相关系数矩阵
        corr_df = self.df[numeric_cols].corr()
        print(corr_df)

        fig = px.imshow(
            corr_df,
            text_auto=".2f",  # 显示两位小数
            aspect="auto",
            title=title,
            color_continuous_scale='RdBu',  # 红蓝配色方案
            zmin=-1,  # 最小相关系数
            zmax=1  # 最大相关系数
        )

        # 保存图像（可选）
        # fig.write_image("correlation_heatmap.png")

        return fig

if __name__ == '__main__':
    df = pd.read_excel('../uploads/data2_1.xlsx')
    visualizer = DataVisualizer(df)
    print(visualizer.get_available_columns())
    print(visualizer.get_numeric_columns())
    print(visualizer.get_categorical_columns())
    # fig1=visualizer.plot_correlation_heatmap()
    # fig1.show()
    # fig2=visualizer.plot_histogram('year',title='Histogram of Age')
    # fig2.show()