import streamlit as st
from datetime import datetime, timedelta
from xml.dom import minidom
import pandas as pd
import sqlite3
import os

# Class for denial
class denial_class:
    
    def __init__(self, tree, root, min, max, db_path, new_source, new_date, file_changed, def_file):

        # Initialize instance variables
        self.tree = tree
        self.root = root
        self.denial_date = None
        self.computer = None
        self.source = None
        self.product = None
        self.created_on = None
        self.updated_on = None
        self.total_denial_count = None
        self.min = min
        self.max = max
        self.new_source = new_source
        self.new_date = new_date
        self.file_changed = file_changed
        self.def_file = def_file
        self.db_path = db_path

        # Determine the table name based on the def_file flag
        if self.def_file is True:
            self.table_name = "default_denial"
        else:
            self.table_name = "denial"
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
            self.connection = sqlite3.connect(self.db_path, timeout = 1)
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
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY,
                denial_date TEXT,
                computer TEXT,
                product TEXT,
                source TEXT,
                sys_created_on TEXT,
                sys_updated_on TEXT,
                total_denial_count TEXT
            )
        ''')
        self.connection.commit()

    #function to clear table in the database 
    def clear_table(self):
        self.delete_table()
        self.insert_data()

    #function to insert data into the database
    def insert_data(self):
        self.cursor.execute(f'SELECT COUNT(*) FROM {self.table_name}')
        rows = self.cursor.fetchone()[0]

        # Insert data into the table
        if rows == 0:
            for elem in self.root.findall('.//samp_eng_app_denial'):
                denial_date = elem.find('denial_date').text
                computer = elem.find('computer').get('display_value')
                product = elem.find('norm_product').get('display_value')
                source = elem.find('source').text
                sys_created_on = elem.find('sys_created_on').text
                sys_updated_on = elem.find('sys_updated_on').text
                total_denial_count = elem.find('total_denial_count').text

                self.cursor.execute(f'''
                                    INSERT INTO {self.table_name}(denial_date, computer, product, source, sys_created_on, sys_updated_on, total_denial_count)
                                    VALUES(?, ?, ?, ?, ?, ?, ?)
                                    ''', (denial_date, computer, product, source, sys_created_on, sys_updated_on, total_denial_count))

        self.connection.commit()

    #function to delete a table into the database
    def delete_table(self):
        self.cursor.execute(f'DELETE FROM {self.table_name}')
        self.create_tables()
        self.connection.commit()

    #function to get all values from the database
    def getall(self):
        self.cursor.execute(f'''SELECT * FROM {self.table_name}''')
        return self.cursor.fetchall()

    #function to close the database connection
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    #function to display the denial data
    def disp_denial(self):   
        col_idx = 0
        cols = st.columns(4)

        self.cursor.execute(f'''SELECT COUNT(*) FROM {self.table_name}''')
        rows = self.cursor.fetchone()[0]

        #getting the values from the database
        denial_date = self.get_denial_date()
        computer = self.get_computer()
        product = self.get_product()
        source = self.get_source()
        sys_created_on = self.get_created_on()
        sys_updated_on = self.get_updated_on()
        total_denial_count = self.get_total_denial_count()
        source = self.get_source()

        #iterating the values to display it to the UI
        for idx in range(0,rows):
            
            display_idx = idx + 1

            if self.min <= display_idx <= self.max:
                
                with cols[col_idx % 4].expander(f"#### Object {display_idx}", expanded=True):
                    st.markdown(f"""
                    **Denial Date**: {denial_date[display_idx]}  
                    **Computer Name**: {computer[display_idx]}  
                    **Product**: {product[display_idx]}  
                    **Source**: {source[display_idx]}  
                    **Created on**: {sys_created_on[display_idx]}  
                    **Updated on**: {sys_updated_on[display_idx]}  
                    **Total Denial Count**: {total_denial_count[display_idx]}  
                    """)

                col_idx += 1

    # SETTERS
    #function to set the value of tree
    def set_tree(self, tree):
        self.tree = tree
    #function to set the value of root
    def set_root(self, root):
        self.root = root
    #function to set the value of denial_date
    def set_denial_date(self, denial_date):
        self.denial_date = denial_date
    #function to set the value of computer
    def set_computer(self, computer):
        self.computer = computer
    #function to set the value of product
    def set_product(self, product):
        self.product = product
    #function to set the value of created_on
    def set_created_on(self, created_on):
        self.created_on = created_on
    #function to set the value of updated_on
    def set_updated_on(self, updated_on):
        self.updated_on = updated_on
    #function to set the value of total denial count
    def set_total_denial_count(self, total_denial_count):
        self.total_denial_count = total_denial_count
    #function to set the value of min
    def set_min(self, min):
        self.min = min
    #function to set the value of max
    def set_max(self, max):
        self.max = max
    #function to set the value of new_source
    def set_new_source(self, new_source):
        self.new_source = new_source
    #function to set the value of new_date
    def set_new_date(self, new_date):
        self.new_date = new_date

    # GETTERS
    #function to get the value of tree
    def get_tree(self):
        return self.tree
    #function to get the value of root
    def get_root(self):
        return self.root
    #function to get the value of denial date from database (return dict)
    def get_denial_date(self):
        
        self.cursor.execute(f'''
        SELECT id, denial_date FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.denial_date      
        self.denial_date = {row[0]: row[1] for row in rows}

        return self.denial_date
    #function to get the value of computer from database (return dict)
    def get_computer(self):
    
        self.cursor.execute(f'''
        SELECT id, computer FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.computer = {row[0]: row[1] for row in rows}

        return self.computer
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
    #function to get the value of product from database (return dict)
    def get_product(self):

        self.cursor.execute(f'''
        SELECT id, product FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.product      
        self.product = {row[0]: row[1] for row in rows}

        return self.product
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
    #function to get the value of total denial count from database (return dict)
    def get_total_denial_count(self):

        self.cursor.execute(f'''
        SELECT id, total_denial_count FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.total_denial_count      
        self.total_denial_count = {row[0]: row[1] for row in rows}
        return self.total_denial_count

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

    # UPDATE
    #function to update source value of the database
    def update_denial_source(self):
        if self.new_source is not None:
            self.cursor.execute(f'''
            UPDATE {self.table_name}
            SET source = ?
            WHERE id BETWEEN ? AND ?
            ''', (self.new_source, self.min, self.max))
            self.connection.commit()
        else:
            source_values = self.get_source(self.min)
            self.cursor.execute(f'''
            UPDATE {self.table_name}
            SET source = ?
            WHERE id BETWEEN ? AND ?
            ''', (source_values, self.min, self.max))
        self.connection.commit()
    #function to update denial_date value of the database
    def update_denial_date(self):
        error = False 
        if self.new_date is not None:

            self.denial_date = self.get_denial_date()
            min = self.min
            
            for idx, date_str in self.denial_date.items():
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
                            SET denial_date = ?
                            WHERE id = ?
                        ''', (new_date1_str, idx))
                            
                        except ValueError as e:
                            # Handle errors if date parsing fails
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    
                    else: 
                        # If the date string is None, update the record with the new date
                        min = min + 1
                        self.cursor.execute('''
                        UPDATE denial
                        SET denial_date = ?
                        WHERE id = ?
                    ''', (self.new_date.strftime('%Y-%m-%d'), idx))
                    
            self.connection.commit()
        return error
    #function to parse the denial file into xml file
    def denial_parser(self):

        self.cursor.execute(f'''SELECT id, source FROM {self.table_name}''',)
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()
        # Extract the single column from the rows and store it in self.source        
        new_source = {row[0]: row[1] for row in rows}

        self.cursor.execute(f'''SELECT id, denial_date FROM {self.table_name}''',)
        rows1 = self.cursor.fetchall()
        new_date = {row[0]: row[1] for row in rows1}

        for idx, elem in enumerate(self.root.findall('.//samp_eng_app_denial'), 1):

            source = elem.find('source')
            source.text = new_source[idx]
            denial_date = elem.find('denial_date')
            denial_date.text = new_date[idx]
    
        return self.tree
    #to test if it is updating in the database
    def test(self):
        self.cursor.execute('''SELECT * FROM denial''')
        result = self.cursor.fetchall()
        return result
