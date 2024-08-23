import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os
#class for concurrent
class concurrent_class:

    def __init__(self,tree,root,min,max,db_path,new_source,new_date,file_changed):

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
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        """Initialize the database and create tables if they don't exist."""
        if not os.path.exists(self.db_path):
            # Create a new database file and establish a connection
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            print(f"Database '{self.db_path}' created.")
            # Create tables
            
        else:
            # Connect to the existing database
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            print(f"Connected to the existing database '{self.db_path}'.")
            
        self.create_tables()
        if self.file_changed:    
            self.clear_table()
        else:
            self.insert_data()

    def create_tables(self):
        """Create tables if they do not exist."""
        # Creating the 'concurrent' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS concurrent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conc_usage_id TEXT,
                concurrent_usage INTEGER,
                license TEXT,
                license_name TEXT,
                source TEXT,
                sys_created_by TEXT,
                sys_created_on TEXT,
                sys_domain TEXT,
                sys_domain_path TEXT,
                sys_id TEXT,
                sys_mod_count INTEGER,
                sys_updated_by TEXT,
                sys_updated_on TEXT,
                usage_date TEXT
            )
        ''')
        self.connection.commit()

    def clear_table(self):
        self.cursor.execute('DROP TABLE IF EXISTS concurrent')
        self.create_tables()
        self.cursor.execute('DELETE FROM sqlite_sequence WHERE name="concurrent"')
        self.insert_data()
        
    def insert_data(self):
        """Insert data from XML into the 'concurrent' table."""
        self.cursor.execute("PRAGMA table_info(concurrent)")
        columns = [row[1] for row in self.cursor.fetchall()]
        columns_str = ', '.join([f'"{col}"' for col in columns])
        placeholders = ', '.join(['?'] * len(columns))
        insert_query = f'INSERT INTO concurrent ({columns_str}) VALUES ({placeholders})'

        self.cursor.execute('SELECT COUNT(*) FROM concurrent')
        rows = self.cursor.fetchone()[0]
        # Insert data into the table
        if rows == 0:
            for elem in self.root.findall('.//samp_eng_app_concurrent_usage'):
                data = []
                for col in columns:
                    if col == 'id':
                        # Handle the 'id' column; usually, this is an auto-incremented field
                        value = None
                    elif col.endswith('_name'):
                        # Handle columns that map to display_value attributes
                        element_name = col.replace('_name', '')
                        element = elem.find(element_name)
                        value = element.get('display_value') if element is not None else ''
                    else:
                        value = elem.find(col).text if elem.find(col) is not None else ''
                        if col == 'concurrent_usage' and value.isdigit():
                            value = int(value)
                        if col == 'sys_mod_count' and value.isdigit():
                            value = int(value)
    
                    data.append(value)
    
                self.cursor.execute(insert_query, data)

        self.connection.commit()
        
    def test(self):
        self.cursor.execute('''SELECT * FROM concurrent WHERE id = 1''')
        result = self.cursor.fetchall()
        return result
        
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")   

    #SETTERS
    def set_tree(self, tree):
        self.tree = tree
    
    def set_root(self,root):
        self.root = root
    
    def set_min(self,min):
        self.min = min
    
    def set_max(self,max):
        self.max = max
    
    def set_new_source(self,new_source):
        self.new_source = new_source

    def set_new_date(self,new_date):
        self.new_date = new_date

    def set_License_Name(self, license_name):
        self.license_name = license_name
    
    def set_source(self,source):
        self.source = source

    def set_usage_date(self,usage_date):
        self.usage_date = usage_date

    def set_created_on(self,created_on):
        self.created_on = created_on
    
    def set_updated_on(self,updated_on):
        self.updated_on = updated_on

    def set_concurrent_usage(self,concurrent_usage):
        self.concurrent_usage = concurrent_usage


    #GETTERS
    def get_tree(self):
        return self.tree 
    
    def get_root(self):
        return self.root
    
    def get_min(self):
        return self.min
    
    def get_max(self):
        return self.max
    
    def get_new_source(self):
        return self.new_source

    def get_new_date(self):
        return self.new_date 

    def get_license_name(self):

        self.cursor.execute('''
        SELECT id, license_name FROM concurrent
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.license_name = {row[0]: row[1] for row in rows}

        return self.license_name
    
    def get_source(self):

        self.cursor.execute('''
        SELECT id, source FROM concurrent
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.source = {row[0]: row[1] for row in rows}
        return self.source

    def get_usage_date(self):
        self.cursor.execute('''
        SELECT id, usage_date FROM concurrent
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.usage_date = {row[0]: row[1] for row in rows}
        return self.usage_date 

    def get_created_on(self):
        self.cursor.execute('''
        SELECT id, sys_created_on FROM concurrent
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.created_on = {row[0]: row[1] for row in rows}
        return self.created_on 
    
    def get_updated_on(self):
        self.cursor.execute('''
        SELECT id, sys_updated_on FROM concurrent
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.updated_on = {row[0]: row[1] for row in rows}
        return self.updated_on 

    def get_concurrent_usage(self):
        self.cursor.execute('''
        SELECT id, concurrent_usage FROM concurrent
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.concurrent_usage = {row[0]: row[1] for row in rows}
        return self.concurrent_usage

    #UPDATE
    def update_concurrent_source(self):

        if self.new_source is not None:
            self.cursor.execute('''
            UPDATE concurrent
            SET source = ?
            WHERE id BETWEEN ? AND ?
        ''', (self.new_source, self.min, self.max))
            self.connection.commit()
        elif self.new_source == "" or self.new_source is None:
            self.source = self.get_source()
            for value in self.source.values():
                self.cursor.execute('''
                UPDATE concurrent
                SET source = ?
                WHERE id BETWEEN ? AND ?
            ''', (value, self.min, self.max))

    def update_concurrent_date(self):
        error = False 
        if self.new_date is not None:

            self.usage_date = self.get_usage_date()
            min = self.min
            
            for idx, date_str in self.usage_date.items():
                if self.min <= idx <= self.max:
                    if date_str is not None:
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                            new_date_obj = self.new_date - date_obj
                            
                            if idx == min:
                                # Calculate the interval days
                                interval_days = new_date_obj.days
                                min = -1
                                # Adjust the date by adding the interval days to the original date
                            new_date1 = date_obj + timedelta(days=interval_days)
                            new_date1_str = new_date1.strftime('%Y-%m-%d')
    
                            self.cursor.execute('''
                            UPDATE concurrent
                            SET usage_date = ?
                            WHERE id = ?
                        ''', (new_date1_str, idx))
                            
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    
                    else: 
                        min = min + 1
                        self.cursor.execute('''
                        UPDATE concurrent
                        SET usage_date = ?
                        WHERE id = ?
                    ''', (self.new_date.strftime('%Y-%m-%d'), idx))
                    
            self.connection.commit()
        return error

    def disp_concurrent(self):

        col_idx = 0
        cols = st.columns(4)

        usage_date = self.get_usage_date()
        license_name = self.get_license_name()
        source = self.get_source()
        sys_created_on = self.get_created_on()
        sys_updated_on = self.get_updated_on()
        concurrent_usage = self.get_concurrent_usage()
        for idx in range(len(usage_date)):
            
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
                
    def concurrent_parser(self):

        new_source = self.get_source()
        new_date = self.get_usage_date()

        for idx, elem in enumerate(self.root.findall('.//samp_eng_app_concurrent_usage'), 1):

            source = elem.find('source')
            source.text = new_source[idx]
            usage_date = elem.find('usage_date')
            usage_date.text = new_date[idx]
    
        return self.tree


    def test(self):
        self.cursor.execute('''SELECT * FROM concurrent''')
        result = self.cursor.fetchall()
        return result


    
