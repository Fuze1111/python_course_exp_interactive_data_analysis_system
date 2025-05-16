
class DataManagement:
    """
    数据管理类
    """
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = None
        self.ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}



