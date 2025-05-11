import pandas as pd
import pymysql

class data_management:
    def __init__(self, data_path):
        self.data_path = data_path

    def upload_data(self):
        """
        Uploads data from the specified path.
        """
        try:
            if self.data_path.endswith('.csv'):
                self.data = pd.read_csv(self.data_path)
            elif self.data_path.endswith('.xlsx'):
                self.data = pd.read_excel(self.data_path)
            print("Data uploaded successfully.")
        except Exception as e:
            print(f"Error uploading data: {e}")

        return self.data

    def preview_data(self, n=5):
        """
        Previews the first n rows of the data.
        """
        try:
            return self.data.head(n)
        except AttributeError:
            print("No data to preview. Please upload data first.")
            return None

    def save_data(self, save_path):
        """
        Saves the data to the specified path.
        """
        try:
            if save_path.endswith('.csv'):
                self.data.to_csv(save_path, index=False)
            elif save_path.endswith('.xlsx'):
                self.data.to_excel(save_path, index=False)
            print("Data saved successfully.")
        except Exception as e:
            print(f"Error saving data: {e}")

    