#封装机器学习算法
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error, accuracy_score, silhouette_score


class DataAnalyzer:
    """
    数据分析类：封装了聚类、分类、预测和降维等功能
    """

    def __init__(self, data):
        """
        初始化数据分析器

        参数:
            data: pandas DataFrame 对象
        """
        self.data = data
        self.model = None
        self.scaler = StandardScaler()

    def preprocess_data(self, features, target=None, test_size=0.2, random_state=42):
        """
        数据预处理：划分训练集和测试集，并进行特征标准化

        参数:
            features: 特征列名列表
            target: 目标变量列名（分类/预测时需要）
            test_size: 测试集比例
            random_state: 随机种子
        """
        X = self.data[features]
        X_scaled = self.scaler.fit_transform(X)

        if target:
            y = self.data[target]
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=random_state
            )
            return X_train, X_test, y_train, y_test, X_scaled

        return X_scaled

    def cluster_kmeans(self, features, n_clusters=3, random_state=42):
        """
        K-means聚类

        参数:
            features: 用于聚类的特征列名列表
            n_clusters: 聚类数量
            random_state: 随机种子

        返回:
            带有聚类标签的DataFrame
        """
        X_scaled = self.preprocess_data(features)

        # 训练K-means模型
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state)
        cluster_labels = self.model.fit_predict(X_scaled)

        # 计算轮廓系数评估聚类效果
        silhouette_avg = silhouette_score(X_scaled, cluster_labels)

        # 将聚类结果添加到原始数据中
        result_df = self.data.copy()
        result_df['cluster'] = cluster_labels

        return {
            'model': self.model,
            'data': result_df,
            'silhouette_score': silhouette_avg,
            'cluster_centers': self.model.cluster_centers_
        }

    def cluster_dbscan(self, features, eps=0.5, min_samples=5):
        """
        DBSCAN聚类(密度聚类)

        参数:
            features: 用于聚类的特征列名列表
            eps: 邻域半径
            min_samples: 核心对象的最小样本数

        返回:
            带有聚类标签的DataFrame
        """
        X_scaled = self.preprocess_data(features)

        # 训练DBSCAN模型
        self.model = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = self.model.fit_predict(X_scaled)

        # 计算轮廓系数评估聚类效果(如果不止一个聚类)
        silhouette_avg = None
        if len(set(cluster_labels)) > 1 and -1 not in cluster_labels:
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)

        # 将聚类结果添加到原始数据中
        result_df = self.data.copy()
        result_df['cluster'] = cluster_labels

        return {
            'model': self.model,
            'data': result_df,
            'silhouette_score': silhouette_avg,
            'n_clusters': len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        }

    def classify(self, features, target, test_size=0.2, random_state=42):
        """
        随机森林分类

        参数:
            features: 特征列名列表
            target: 目标变量列名
            test_size: 测试集比例
            random_state: 随机种子

        返回:
            分类模型和评估结果
        """
        X_train, X_test, y_train, y_test, _ = self.preprocess_data(
            features, target, test_size, random_state
        )

        # 训练随机森林分类器
        self.model = RandomForestClassifier(random_state=random_state)
        self.model.fit(X_train, y_train)

        # 预测和评估
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        # 特征重要性
        feature_importance = dict(zip(features, self.model.feature_importances_))

        return {
            'model': self.model,
            'accuracy': accuracy,
            'feature_importance': feature_importance,
            'y_test': y_test,
            'y_pred': y_pred
        }

    def predict(self, features, target, test_size=0.2, random_state=42, method='linear'):
        """
        回归预测

        参数:
            features: 特征列名列表
            target: 目标变量列名
            test_size: 测试集比例
            random_state: 随机种子
            method: 预测方法 ('linear' 或 'random_forest')

        返回:
            预测模型和评估结果
        """
        X_train, X_test, y_train, y_test, _ = self.preprocess_data(
            features, target, test_size, random_state
        )

        # 选择回归模型
        if method == 'linear':
            self.model = LinearRegression()
        elif method == 'random_forest':
            self.model = RandomForestRegressor(random_state=random_state)
        else:
            raise ValueError("不支持的预测方法，请使用 'linear' 或 'random_forest'")

        # 训练模型
        self.model.fit(X_train, y_train)

        # 预测和评估
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = self.model.score(X_test, y_test)

        # 特征重要性(对随机森林有效)
        feature_importance = None
        if method == 'random_forest':
            feature_importance = dict(zip(features, self.model.feature_importances_))

        return {
            'model': self.model,
            'mse': mse,
            'r2': r2,
            'feature_importance': feature_importance,
            'y_test': y_test,
            'y_pred': y_pred
        }

    def dimensionality_reduction(self, features, n_components=2):
        """
        使用PCA进行降维

        参数:
            features: 用于降维的特征列名列表
            n_components: 降维后的维度

        返回:
            降维后的数据和PCA模型
        """
        X_scaled = self.preprocess_data(features)

        # 执行PCA降维
        self.model = PCA(n_components=n_components)
        X_reduced = self.model.fit_transform(X_scaled)

        # 创建降维后的DataFrame
        reduced_df = pd.DataFrame(
            X_reduced,
            columns=[f'PC{i + 1}' for i in range(n_components)]
        )

        # 计算各主成分的解释方差比例
        explained_variance = {
            'components': [f'PC{i + 1}' for i in range(n_components)],
            'explained_variance_ratio': self.model.explained_variance_ratio_,
            'cumulative_variance_ratio': np.cumsum(self.model.explained_variance_ratio_)
        }

        return {
            'model': self.model,
            'reduced_data': reduced_df,
            'explained_variance': explained_variance,
            'feature_weights': pd.DataFrame(
                self.model.components_,
                columns=features,
                index=[f'PC{i + 1}' for i in range(n_components)]
            )
        }
