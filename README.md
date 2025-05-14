# 文件数据分析与可视化综合应用
## Web页面
⏲  使用Bootstrap响应式布局，Flask框架实现数据分析与可视化的Web应用。  
You can change this with other frameworks like Django, Streamlit, etc.
But you must write the expression when pushing.
### 1.1 base界面
### 1.2 文件上传
#### 
DataUploader封装
### 1.3 数据清洗
Z分数（Z-Score）表示一个数据点与数据集均值之间的距离（以标准差为单位）。其公式为：
$$Z=\frac{X-\mu}{\sigma}$$Z分数的结果是一个无量纲值，表示数据点在分布中的相对位置。  
在正态分布中，约99.7%的数据点的Z分数在[-3, 3]范围内。超出此范围的点可能被标记为异常值。
### 1.4 数据分析
### 1.5 数据可视化

--- 
### 运行
```bash
cd /path/to/your/project
source venv/bin/activate
pip install -r requirements.txt 
python app.py  
```
Click link like `http://127.0.0.1:5000/`  
If you find pip install error, please use `pip install -r requirements.txt --no-deps` to install the packages one by one.  
🤚Or you can exchange pip source to avoid cache issues.

---
## Python后端
### 2.1 Flask框架
### 2.2 数据处理
### 2.3 数据分析
### 2.4 数据可视化

---
## 任务要求
| 模块       | 必做要求                                       | 扩展建议                              |
|------------|------------------------------------------------|------------------------------------------------|
| 数据管理   | 支持 CSV/Excel 等文件上传、预览、导出         | 数据库集成（SQLite/MySQL）                     |
| 数据清洗   | 缺失值处理、异常值检测                         | 自动化清洗规则配置                             |
| 可视化     | 动态生成 3 种以上图表                          | 用户自定义图表参数                             |
| 分析功能   | 至少实现 1 种分析（聚类 / 预测 / 分类 / 降维） | 多算法对比 + 效果评估                          |
| Web 界面   | 响应式布局，基础交互                           | 多用户登录、历史记录存储、检索等管理功能       |


---
### 上传git
✅运行desktop，点击上传文件，**只需**上传.py / .html/ .txt/ css/ js等文件  
❌由于python，packages的版本可能不同，**无需**上传/.idea文件夹 /.pyc 文件


