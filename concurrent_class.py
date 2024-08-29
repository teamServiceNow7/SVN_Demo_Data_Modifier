import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os
#class for concurrent
class concurrent_class:

    def __init__(self,tree,root,min,max,db_path,new_source,new_date,file_changed, def_file):
    
        # Initialize instance variables
        self.tree = tree
        self.root = root
        self.min = min
        self.max = max
        self.new_source = new_source
        self.new_date = new_date
        self.license_name = None
        self.normalized_name = None
        self.source = None
        self.concurrent_usage = None
        self.usage_date = None
        self.created_on = None
        self.updated_on = None
        self.file_changed = file_changed
        self.def_file = def_file
        self.db_path = db_path

        # Determine the table name based on the def_file flag
        if self.def_file is True:
            self.table_name = "default_concurrent"
        else:
            self.table_name = "concurrent"
        # Initialize the database
        self.initialize_database()

    #Function to initialize database
    def initialize_database(self):
        """Initialize the database and create tables if they don't exist."""
        # Check if the database file already exists
        if not os.path.exists(self.db_path):
            # If the database file does not exist, create a new file and establish a connection
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            print(f"Database '{self.db_path}' created.")
           
        else:
            # If the database file exists, connect to the existing database
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            print(f"Connected to the existing database '{self.db_path}'.")
        # Create tables 
        self.create_tables()
        # Check if the file has changed
        if self.file_changed:   
            # If the file has changed, clear the existing table data
            self.clear_table()
        else:
            # If the file has not changed, insert new data into the table
            self.insert_data()

    #function to create tables in the database
    def create_tables(self):
        """Create tables if they do not exist."""
        # Creating the 'concurrent' table
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usage_date TEXt,
                license_name TEXT,
                source TEXT,
                sys_created_on TEXT,
                sys_updated_on TEXT,
                concurrent_usage TEXT
            )
        ''')
        self.connection.commit()
        
    #function to clear table in the database 
    def clear_table(self):
        self.cursor.execute(f'DROP TABLE IF EXISTS {self.table_name}')
        self.create_tables()
        self.cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{self.table_name}"')
        self.insert_data()
    #function to insert data into the database
    def insert_data(self):
        self.cursor.execute(f'SELECT COUNT(*) FROM {self.table_name}')
        rows = self.cursor.fetchone()[0]

        # Insert data into the table
        if rows == 0:
            for elem in self.root.findall('.//samp_eng_app_concurrent_usage'):
                usage_date = elem.find('usage_date').text
                license_name = elem.find('license').get('display_value')
                source = elem.find('source').text
                sys_created_on = elem.find('sys_created_on').text
                sys_updated_on = elem.find('sys_updated_on').text
                concurrent_usage = elem.find('concurrent_usage').text

                self.cursor.execute(f'''
                                    INSERT INTO {self.table_name}(usage_date, license_name, source, sys_created_on, sys_updated_on, concurrent_usage)
                                    VALUES(?, ?, ?, ?, ?, ?)
                                    ''', (usage_date, license_name, source, sys_created_on, sys_updated_on, concurrent_usage))

        self.connection.commit()
    #function to close the database connection        
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")   

    #SETTERS
    #function to set the value of tree
    def set_tree(self, tree):
        self.tree = tree
    #function to set the value of root
    def set_root(self,root):
        self.root = root
    #function to set the value of min
    def set_min(self,min):
        self.min = min
    #function to set the value of max
    def set_max(self,max):
        self.max = max
    #function to set the value of new_source
    def set_new_source(self,new_source):
        self.new_source = new_source
    #function to set the value of new_date
    def set_new_date(self,new_date):
        self.new_date = new_date
    #function to set the value of license name
    def set_License_Name(self, license_name):
        self.license_name = license_name
    #function to set the value of source
    def set_source(self,source):
        self.source = source
    #function to set the value of usage_date
    def set_usage_date(self,usage_date):
        self.usage_date = usage_date
    #function to set the value of created_on
    def set_created_on(self,created_on):
        self.created_on = created_on
    #function to set the value of updated_on
    def set_updated_on(self,updated_on):
        self.updated_on = updated_on
    #function to set the value of concurrent usage
    def set_concurrent_usage(self,concurrent_usage):
        self.concurrent_usage = concurrent_usage


    #GETTERS
    #function to get the value of tree
    def get_tree(self):
        return self.tree 
    #function to get the value of root
    def get_root(self):
        return self.root
    #function to get the value of min
    def get_min(self):
        return self.min
    #function to get the value of max
    def get_max(self):
        return self.max
    #function to get the value of new_source
    def get_new_source(self):
        return self.new_source
    #function to get the value of new_date
    def get_new_date(self):
        return self.new_date 
    #function to get the value of license name from database (return dict)
    def get_license_name(self):

        self.cursor.execute(f'''
        SELECT id, license_name FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.license_name      
        self.license_name = {row[0]: row[1] for row in rows}

        return self.license_name
    #function to get the value of source from database (return dict)
    def get_source(self):

        self.cursor.execute(f'''
        SELECT id, source FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.source      
        self.source = {row[0]: row[1] for row in rows}
        return self.source
    #function to get the value of usage date from database (return dict)
    def get_usage_date(self):
        self.cursor.execute(f'''
        SELECT id, usage_date FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.usage_date      
        self.usage_date = {row[0]: row[1] for row in rows}
        return self.usage_date 
    #function to get the value of created_on from database (return dict)
    def get_created_on(self):
        self.cursor.execute(f'''
        SELECT id, sys_created_on FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.created_on      
        self.created_on = {row[0]: row[1] for row in rows}
        return self.created_on 
    #function to get the value of updated_on from database (return dict)
    def get_updated_on(self):
        self.cursor.execute(f'''
        SELECT id, sys_updated_on FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.updated_on      
        self.updated_on = {row[0]: row[1] for row in rows}
        return self.updated_on 
    #function to get the value of concurrent_usage from database (return dict)
    def get_concurrent_usage(self):
        self.cursor.execute(f'''
        SELECT id, concurrent_usage FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.concurrent_usage      
        self.concurrent_usage = {row[0]: row[1] for row in rows}
        return self.concurrent_usage

    #UPDATE
    #function to update source value of the database
    def update_concurrent_source(self):

        if self.new_source is not None:
            self.cursor.execute(f'''
            UPDATE {self.table_name}
            SET source = ?
            WHERE id BETWEEN ? AND ?
        ''', (self.new_source, self.min, self.max))
            self.connection.commit()
        else:
            self.source = self.get_source()
            for value in self.source.values():
                self.cursor.execute(f'''
                UPDATE {self.table_name}
                SET source = ?
                WHERE id BETWEEN ? AND ?
            ''', (value, self.min, self.max))
    #function to update concurrent date value of the database
    def update_concurrent_date(self):
        error = False 
        if self.new_date is not None:

            self.usage_date = self.get_usage_date()
            min = self.min
            
            for idx, date_str in self.usage_date.items():
                 # Iterate through each item in the denial_date dictionary
                # `idx` is the index or ID, `date_str` is the date string associated with that index
                if self.min <= idx <= self.max: # Check if the index is within the specified range [min, max]
                    # Ensure that the date string is not None
                    if date_str is not None:
                        try:
                            # parse the date string into a date object
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                            # Calculate the difference between the new date and the parsed date
                            new_date_obj = self.new_date - date_obj
                            
                            if idx == min:
                                # Calculate the interval days
                                interval_days = new_date_obj.days
                                min = -1
                                # Adjust the date by adding the interval days to the original date
                            new_date1 = date_obj + timedelta(days=interval_days)
                            new_date1_str = new_date1.strftime('%Y-%m-%d')
                            # Update the database record with the new adjusted date
                            self.cursor.execute(f'''
                            UPDATE {self.table_name}
                            SET usage_date = ?
                            WHERE id = ?
                        ''', (new_date1_str, idx))
                            
                        except ValueError as e:
                            # Handle errors if date parsing fails
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    
                    else: 
                        # If the date string is None, update the record with the new date
                        min = min + 1
                        self.cursor.execute(f'''
                        UPDATE {self.table_name}
                        SET usage_date = ?
                        WHERE id = ?
                    ''', (self.new_date.strftime('%Y-%m-%d'), idx))
                    
            self.connection.commit()
        return error
    #function to display the concurrent data
    def disp_concurrent(self):

        col_idx = 0
        cols = st.columns(4)
        self.cursor.execute(f'''SELECT COUNT(*) FROM {self.table_name}''')
        rows = self.cursor.fetchone()[0]
        #getting the values from the database
        usage_date = self.get_usage_date()
        license_name = self.get_license_name()
        source = self.get_source()
        sys_created_on = self.get_created_on()
        sys_updated_on = self.get_updated_on()
        concurrent_usage = self.get_concurrent_usage()
        #iterating the values to display it to the UI
        for idx in range(0,rows):
            
            display_idx = idx + 1

            if self.min <= display_idx <= self.max:
                with cols[col_idx % 4].expander(f"#### Object {display_idx}", expanded=True):
                    st.markdown(f"""
                    **Usage Date**: {usage_date[display_idx]}  
                    **License Name**: {license_name[display_idx]}  
                    **Source**: {source[display_idx]}  
                    **Created on**: {sys_created_on[display_idx]}  
                    **Updated on**: {sys_updated_on[display_idx]}  
                    **Concurrent Usage**: {concurrent_usage[display_idx]}  
                    """)

                col_idx += 1
    #function to parse the concurrent file into xml file
    def concurrent_parser(self):

        self.cursor.execute(f'''SELECT id, source FROM {self.table_name}''',)
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()
        # Extract the single column from the rows and store it in self.source        
        new_source = {row[0]: row[1] for row in rows}

        self.cursor.execute(f'''SELECT id, usage_date FROM {self.table_name}''',)
        rows1 = self.cursor.fetchall()
        new_date = {row[0]: row[1] for row in rows1}

        for idx, elem in enumerate(self.root.findall('.//samp_eng_app_concurrent_usage'), 1):

            source = elem.find('source')
            source.text = new_source[idx]
            usage_date = elem.find('usage_date')
            usage_date.text = new_date[idx]
    
        return self.tree
        
    #to test if it is updating in the database
    def test(self):
        self.cursor.execute(f'''SELECT * FROM {self.table_name}''')
        result = self.cursor.fetchall()
        return result


    
