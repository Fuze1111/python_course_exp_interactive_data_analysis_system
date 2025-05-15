# 绘图（Matplotlib/Plotly）
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Union
from plotly.subplots import make_subplots
import numpy as np


class DataVisualizer:
    """
    用于数据可视化的工具类，支持生成多种类型的图表。
    """

    def __init__(self, df: pd.DataFrame):
        """
        初始化DataVisualizer类。

        参数:
            df (pd.DataFrame): 用于可视化的DataFrame
        """
        self.df = df
        self.numeric_dtypes = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

    def get_available_columns(self) -> list:
        """获取DataFrame中所有列的名称"""
        return self.df.columns.tolist()

    def get_numeric_columns(self) -> list:
        """获取DataFrame中所有数值类型列的名称"""
        return self.df.select_dtypes(include=self.numeric_dtypes).columns.tolist()

    def get_categorical_columns(self) -> list:
        """获取DataFrame中所有分类类型列的名称"""
        return self.df.select_dtypes(include=['object', 'category']).columns.tolist()

    def plot_histogram(self, column: str, nbins: int = None, color_column: str = None, title: str = None) -> go.Figure:
        """
        生成直方图

        参数:
            column (str): 要绘制直方图的数据列
            nbins (int, optional): 直方图的箱数
            color_column (str, optional): 用于颜色编码的列
            title (str, optional): 图表标题

        返回:
            go.Figure: Plotly图形对象
        """
        if column not in self.df.columns:
            raise ValueError(f"列 '{column}' 不存在于DataFrame中")

        if color_column and color_column not in self.df.columns:
            raise ValueError(f"颜色列 '{color_column}' 不存在于DataFrame中")

        fig = px.histogram(
            self.df,
            x=column,
            nbins=nbins,
            color=color_column,
            title=title or f"直方图: {column}",
            barmode='overlay' if color_column else 'relative'
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis_title=column,
            yaxis_title="频率"
        )

        return fig

    def plot_scatter(self, x_column: str, y_column: str, color_column: str = None,
                     size_column: str = None, title: str = None) -> go.Figure:
        """
        生成散点图

        参数:
            x_column (str): X轴数据列
            y_column (str): Y轴数据列
            color_column (str, optional): 用于颜色编码的列
            size_column (str, optional): 用于标记大小的列
            title (str, optional): 图表标题

        返回:
            go.Figure: Plotly图形对象
        """
        for col in [x_column, y_column]:
            if col not in self.df.columns:
                raise ValueError(f"列 '{col}' 不存在于DataFrame中")

        if color_column and color_column not in self.df.columns:
            raise ValueError(f"颜色列 '{color_column}' 不存在于DataFrame中")

        if size_column and size_column not in self.df.columns:
            raise ValueError(f"大小列 '{size_column}' 不存在于DataFrame中")

        fig = px.scatter(
            self.df,
            x=x_column,
            y=y_column,
            color=color_column,
            size=size_column,
            title=title or f"散点图: {x_column} vs {y_column}",
            hover_data=[col for col in [x_column, y_column, color_column, size_column] if col is not None]
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis_title=x_column,
            yaxis_title=y_column
        )

        return fig

    def plot_line(self, x_column: str, y_columns: Union[str, list], color_column: str = None,
                  title: str = None, markers: bool = False) -> go.Figure:
        """
        生成折线图

        参数:
            x_column (str): X轴数据列
            y_columns (str | list): Y轴数据列或列列表
            color_column (str, optional): 用于颜色编码的列
            title (str, optional): 图表标题
            markers (bool, optional): 是否显示标记点

        返回:
            go.Figure: Plotly图形对象
        """
        if x_column not in self.df.columns:
            raise ValueError(f"列 '{x_column}' 不存在于DataFrame中")

        if isinstance(y_columns, str):
            y_columns = [y_columns]

        for col in y_columns:
            if col not in self.df.columns:
                raise ValueError(f"列 '{col}' 不存在于DataFrame中")

        if color_column and color_column not in self.df.columns:
            raise ValueError(f"颜色列 '{color_column}' 不存在于DataFrame中")

        # 如果提供了多个y列，创建一个长格式的DataFrame
        if len(y_columns) > 1:
            df_melted = pd.melt(self.df, id_vars=[x_column], value_vars=y_columns)
            fig = px.line(
                df_melted,
                x=x_column,
                y='value',
                color='variable',
                title=title or f"折线图: {', '.join(y_columns)} vs {x_column}",
                markers=markers
            )
        else:
            fig = px.line(
                self.df,
                x=x_column,
                y=y_columns[0],
                color=color_column,
                title=title or f"折线图: {y_columns[0]} vs {x_column}",
                markers=markers
            )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis_title=x_column,
            yaxis_title=", ".join(y_columns) if len(y_columns) > 1 else y_columns[0]
        )

        return fig

    def plot_bar(self, x_column: str, y_column: str, color_column: str = None,
                 title: str = None, orientation: str = 'v', barmode: str = 'group') -> go.Figure:
        """
        生成柱状图

        参数:
            x_column (str): X轴数据列
            y_column (str): Y轴数据列
            color_column (str, optional): 用于颜色编码的列
            title (str, optional): 图表标题
            orientation (str, optional): 方向 ('v' 或 'h')
            barmode (str, optional): 柱状图模式 ('group', 'stack', 'overlay')

        返回:
            go.Figure: Plotly图形对象
        """
        for col in [x_column, y_column]:
            if col not in self.df.columns:
                raise ValueError(f"列 '{col}' 不存在于DataFrame中")

        if color_column and color_column not in self.df.columns:
            raise ValueError(f"颜色列 '{color_column}' 不存在于DataFrame中")

        fig = px.bar(
            self.df,
            x=x_column,
            y=y_column,
            color=color_column,
            title=title or f"柱状图: {y_column} vs {x_column}",
            orientation=orientation,
            barmode=barmode
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis_title=x_column,
            yaxis_title=y_column
        )

        return fig

    def plot_box(self, y_column: str, x_column: str = None, color_column: str = None,
                 title: str = None, notched: bool = False) -> go.Figure:
        """
        生成箱线图

        参数:
            y_column (str): Y轴数据列
            x_column (str, optional): X轴数据列（分类变量）
            color_column (str, optional): 用于颜色编码的列
            title (str, optional): 图表标题
            notched (bool, optional): 是否显示缺口

        返回:
            go.Figure: Plotly图形对象
        """
        if y_column not in self.df.columns:
            raise ValueError(f"列 '{y_column}' 不存在于DataFrame中")

        if x_column and x_column not in self.df.columns:
            raise ValueError(f"列 '{x_column}' 不存在于DataFrame中")

        if color_column and color_column not in self.df.columns:
            raise ValueError(f"颜色列 '{color_column}' 不存在于DataFrame中")

        fig = px.box(
            self.df,
            x=x_column,
            y=y_column,
            color=color_column,
            title=title or f"箱线图: {y_column}",
            notched=notched
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis_title=x_column if x_column else "",
            yaxis_title=y_column
        )

        return fig

    def plot_pie(self, names_column: str, values_column: str,
                 title: str = None, hole: float = 0.0) -> go.Figure:
        """
        生成饼图/圆环图

        参数:
            names_column (str): 类别名称列
            values_column (str): 数值列
            title (str, optional): 图表标题
            hole (float, optional): 圆环图中心的空洞大小 (0-1)

        返回:
            go.Figure: Plotly图形对象
        """
        for col in [names_column, values_column]:
            if col not in self.df.columns:
                raise ValueError(f"列 '{col}' 不存在于DataFrame中")

        # 按名称列分组并汇总数值列
        grouped_df = self.df.groupby(names_column)[values_column].sum().reset_index()

        fig = px.pie(
            grouped_df,
            names=names_column,
            values=values_column,
            title=title or f"饼图: {values_column} by {names_column}",
            hole=hole
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40)
        )

        return fig

    def plot_correlation_heatmap(self, numeric_cols: list = None, title: str = None) -> go.Figure:
        """
        生成相关系数热力图

        参数:
            numeric_cols (list, optional): 要包含的数值列列表，默认为所有数值列
            title (str, optional): 图表标题

        返回:
            go.Figure: Plotly图形对象
        """
        # 获取所有数值列
        all_numeric_cols = self.get_numeric_columns()

        if not all_numeric_cols:
            raise ValueError("DataFrame中没有找到数值列")

        # 如果没有指定列，则使用所有数值列
        if numeric_cols is None:
            numeric_cols = all_numeric_cols
        else:
            # 验证所有指定的列都是数值列
            invalid_cols = [col for col in numeric_cols if col not in all_numeric_cols]
            if invalid_cols:
                raise ValueError(f"以下列不是数值列: {', '.join(invalid_cols)}")

        # 计算相关系数矩阵
        corr_matrix = self.df[numeric_cols].corr()

        # 创建热力图
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title=title or "相关系数热力图",
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40)
        )

        return fig