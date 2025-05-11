import pandas as pd
import pymysql

class data_management:
    def __init__(self, data_path):
        self.cursor = None
        self.data_path = data_path
        self.data = None
        self.db_connection = None
        self.table_name = None

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

    def connect_mysql(self, host='localhost', user='root', password='', database='', port=3306):
        """
        Connects to MySQL  database.

        Args:
            host: MySQL server host
            user: MySQL username
            password: MySQL password
            database: Database name
            port: MySQL port (default 3306)

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Connect to MySQL database
            self.db_connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            self.cursor = self.db_connection.cursor()
            print("Connected to MySQL database successfully.")
            return True
        except Exception as e:
            print(f"Error connecting to MySQL database: {e}")
            return False

    def upload_data_to_database(self, table_name):
        """
        Uploads data to the connected MySQL database.

        Args:
            table_name: Name of the table to create/insert data into
        """
        self.table_name = table_name
        try:
            if self.cursor is None:
                print("No database connection. Please connect to a database first.")
                return

            # Create table if it doesn't exist
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join([f"{col} VARCHAR(255)" for col in self.data.columns])}
            )
            """
            self.cursor.execute(create_table_query)

            # Insert data into the table
            for index, row in self.data.iterrows():
                insert_query = f"""
                INSERT INTO {table_name} ({', '.join(self.data.columns)})
                VALUES ({', '.join(['%s'] * len(row))})
                """
                self.cursor.execute(insert_query, tuple(row))

            # Commit the changes
            self.db_connection.commit()
            print(f"Data uploaded to MySQL table '{table_name}' successfully.")
        except Exception as e:
            print(f"Error uploading data to MySQL database: {e}")

    def preview_data_from_database(self,n=5):
        """
        Previews the first n rows of the data from the connected MySQL database.

        Args:
            n: Number of rows to preview
        """
        try:
            if self.cursor is None:
                print("No database connection. Please connect to a database first.")
                return

            select_query = f"SELECT * FROM {self.table_name} LIMIT {n}"
            self.cursor.execute(select_query)
            result = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            df = pd.DataFrame(result, columns=columns)
            return df
        except Exception as e:
            print(f"Error previewing data from MySQL database: {e}")
            return None

    def delete_data_from_database(self):
        """
        Deletes data from the connected MySQL database.
        """
        try:
            if self.cursor is None:
                print("No database connection. Please connect to a database first.")
                return

            delete_query = f"DELETE FROM {self.table_name}"
            self.cursor.execute(delete_query)
            self.db_connection.commit()
            print(f"Data deleted from MySQL table '{self.table_name}' successfully.")
        except Exception as e:
            print(f"Error deleting data from MySQL database: {e}")

    def drop_table(self):
        """
        Drops the table from the connected MySQL database.
        """
        try:
            if self.cursor is None:
                print("No database connection. Please connect to a database first.")
                return

            drop_query = f"DROP TABLE IF EXISTS {self.table_name}"
            self.cursor.execute(drop_query)
            self.db_connection.commit()
            print(f"Table '{self.table_name}' dropped successfully.")
        except Exception as e:
            print(f"Error dropping table from MySQL database: {e}")

    def save_data_from_database(self, save_path):
        """
        Saves the data from the connected MySQL database to the specified path.

        Args:
            save_path: Path to save the data
        """
        try:
            if self.cursor is None:
                print("No database connection. Please connect to a database first.")
                return

            select_query = f"SELECT * FROM {self.table_name}"
            self.cursor.execute(select_query)
            result = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            df = pd.DataFrame(result, columns=columns)

            if save_path.endswith('.csv'):
                df.to_csv(save_path, index=False)
            elif save_path.endswith('.xlsx'):
                df.to_excel(save_path, index=False)
            print("Data saved successfully.")
        except Exception as e:
            print(f"Error saving data from MySQL database: {e}")

    def close_connection(self):
        """
        Closes the database connection.
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.db_connection:
                self.db_connection.close()
            print("Database connection closed.")
        except Exception as e:
            print(f"Error closing database connection: {e}")
