import streamlit as st
from usage_class import usage_class
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import os
#class for denial
class denial_class:
    
    def __init__(self,tree,root,min,max,db_path,new_source,new_date):

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
            self.connection = sqlite3.connect(self.db_path, timeout = 1)
            self.cursor = self.connection.cursor()
            print(f"Connected to the existing database '{self.db_path}'.")
        self.create_tables()
        self.clear_table()

    def create_tables(self):
        """Create tables if they do not exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS denial (
                id INTEGER PRIMARY KEY,
                unload_date TEXT,
                action TEXT,
                additional_key TEXT,
                computer TEXT,
                denial_date TEXT,
                denial_id TEXT,
                discovery_model TEXT,
                "group" TEXT,
                is_product_normalized TEXT,
                last_denial_time TEXT,
                license_server TEXT,
                license_type TEXT,
                norm_product TEXT,
                norm_publisher TEXT,
                product TEXT,
                publisher TEXT,
                source TEXT,
                sys_created_by TEXT,
                sys_created_on TEXT,
                sys_domain TEXT,
                sys_domain_path TEXT,
                sys_id TEXT,
                sys_mod_count TEXT,
                sys_updated_by TEXT,
                sys_updated_on TEXT,
                total_denial_count TEXT,
                "user" TEXT,
                version TEXT,
                workstation TEXT
            )
        ''')
        self.connection.commit()

    def clear_table(self):
        self.insert_data()
        self.delete_table()
        self.insert_data()

    def insert_data(self):
        """Insert data from XML into the database."""
        self.cursor.execute("PRAGMA table_info(denial)")
        columns = [row[1] for row in self.cursor.fetchall()]
        columns_str = ', '.join([f'"{col}"' for col in columns])
        placeholders = ', '.join(['?'] * len(columns))
        insert_query = f'INSERT INTO denial ({columns_str}) VALUES ({placeholders})'

        self.cursor.execute('SELECT COUNT(*) FROM denial')
        rows = self.cursor.fetchone()[0]

        if rows == 0:
            for elem in self.root.findall('.//samp_eng_app_denial'):
                data = []
                for col in columns:
                    if col == 'id':
                        value = int(elem.find(col).text) if elem.find(col) is not None and elem.find(col).text.isdigit() else None
                    else:
                        value = elem.find(col).text if elem.find(col) is not None else ''
                    data.append(value)
                
                self.cursor.execute(insert_query, data)
        self.connection.commit()

    def delete_table(self):
        self.cursor.execute('DELETE FROM denial')

    def getall(self):
        self.cursor.execute('''SELECT * FROM denial''')
        #Save values into arrays

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
            
    def test(self):
        self.cursor.execute('''SELECT * FROM denial WHERE id = 1''')
        result = self.cursor.fetchall()
        return result
        
    #(TO BE DELETED)    
    def update_denial(self):

        st.write("  ")
        cols = st.columns(4)  # Adjust the number of columns as needed
        col_idx = 0
        flag = 2
        value1 = 0
        error = False 
        data = [] #new addition
        for idx, elem in enumerate(self.root.findall('.//samp_eng_app_denial'), 1):
            #Condition for the slider
            if (self.min <= idx <= self.max):
                #to change the source
                if self.new_source:
                    self.source = elem.find('source')  
                    if self.source is not None:
                        self.source.text = self.new_source
                #to change the denial_date
                if self.new_date:
                    self.denial_date = elem.find('denial_date')
                    #condition if the denial_date_elem.text have a value
                    if self.denial_date is not None and self.denial_date.text is not None:
                        try:
                            #calling the function to adjust the usage_date in concurrent
                            value = usage_class.adjust_date_element(None,None,self.denial_date,self.new_date, idx, self.min,flag,value1)
                            #storing the increment date value to use to other iterations
                            value1 = value
                        #catching the errors (this will print if there are wrong format in date)
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    else:
                        #adjusting the min_idle to get the next value if the first value is none
                        min = min+1
                        #replacing all that have the none value into the inputted start date
                        self.denial_date.text = self.new_date.strftime('%Y-%m-%d')

                #new Addition (Dataframe) 
                source = elem.find('source').text
                computer = elem.find('computer').get('display_value')
                product = elem.find('norm_product').get('display_value')
                created_on = elem.find('sys_created_on').text
                updated_on = elem.find('sys_updated_on').text
                denial_count = elem.find('total_denial_count').text
                denial_date = elem.find('denial_date').text
                data.append({'source':source, 'computer': computer,'product':product,'created_on': created_on, 'updated_on': updated_on, 'denial_count':denial_count,'denial_date':denial_date})  
                
                with cols[col_idx % 4].expander(f"#### Object {idx}", expanded=True):
                    st.markdown(f"""
                    **Denial Date**: {elem.find('denial_date').text if elem.find('denial_date') is not None else 'N/A'}  
                    **Computer Name**: {elem.find('computer').get('display_value') if elem.find('computer') is not None else 'N/A'}  
                    **Product**: {elem.find('norm_product').get('display_value') if elem.find('norm_product') is not None else 'N/A'}  
                    **Source**: {elem.find('source').text if elem.find('source') is not None else 'N/A'}  
                    **Created on**: {elem.find('sys_created_on').text if elem.find('sys_created_on') is not None else 'N/A'}  
                    **Updated on**: {elem.find('sys_updated_on').text if elem.find('sys_updated_on') is not None else 'N/A'}  
                    **Total Denial Count**: {elem.find('total_denial_count').text if elem.find('total_denial_count') is not None else 'N/A'}  
                    """)
                col_idx += 1
        df = pd.DataFrame(data)
        print(df)
        return error,self.tree  #can modify because of tree return  
    #(TO BE DELETED)
    def display_data(self):
        data = []

        for idx, elem in enumerate(self.root.findall('.//samp_eng_app_denial'), 1):

            source = elem.find('source').text
            computer = elem.find('computer').get('display_value')
            product = elem.find('norm_product').get('display_value')
            created_on = elem.find('sys_created_on').text
            updated_on = elem.find('sys_updated_on').text
            denial_count = elem.find('total_denial_count').text
            denial_date = elem.find('denial_date').text
            data.append({'source':source, 'computer': computer,'product':product,'created_on': created_on, 'updated_on': updated_on, 'denial_count':denial_count,'denial_date':denial_date}) 
        df = pd.DataFrame(data)
        return df

    #SETTERS
    def set_tree(self,tree):
    
        self.tree = tree

    def set_root(self,root):
    
        self.root = root

    def set_denial_date(self,denial_date):
        
        self.denial_date = denial_date

    def set_computer(self,computer):
    
        self.computer = computer

    def set_product(self,product):

        self.product = product
    
    def set_created_on(self,created_on):
        self.created_on = created_on
    
    def set_updated_on(self,updated_on):

        self.updated_on = updated_on
    
    def set_total_denial_count(self,total_denial_count):

        self.total_denial_count = total_denial_count

    def set_min(self,min):
        self.min = min
    
    def set_max(self,max):
        self.max = max
    
    def set_new_source(self,new_source):

        self.new_source = new_source
    
    def set_new_date(self,new_date):
        self.new_date = new_date

    #GETTERS
    def get_tree(self):
    
       return self.tree

    def get_root(self):
    
        return self.root

    def get_denial_date(self):
        
        self.cursor.execute('''
        SELECT id, denial_date FROM denial
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.denial_date = {row[0]: row[1] for row in rows}

        return self.denial_date

    def get_computer(self):
    
        self.cursor.execute('''
        SELECT id, computer FROM denial
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.computer = {row[0]: row[1] for row in rows}

        return self.computer

    def get_source(self):
 
        self.cursor.execute('''
        SELECT source FROM denial
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
       
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()
 
        # Extract the single column from the rows and store it in self.source        
        self.source = [row[0] for row in rows]
 
        return self.source
    
    def get_product(self):

        self.cursor.execute('''
        SELECT id, product FROM denial
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.product = {row[0]: row[1] for row in rows}

        return self.product
    
    def get_created_on(self):
        self.cursor.execute('''
        SELECT id, sys_created_on FROM denial
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.created_on = {row[0]: row[1] for row in rows}
        return self.created_on
    
    def get_updated_on(self):

        self.cursor.execute('''
        SELECT id, sys_updated_on FROM denial
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.updated_on = {row[0]: row[1] for row in rows}
        return self.updated_on
    
    def get_total_denial_count(self):

        self.cursor.execute('''
        SELECT id, total_denial_count FROM denial
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.total_denial_count = {row[0]: row[1] for row in rows}
        return self.total_denial_count
    
    def get_min(self):
        return self.min 
    
    def get_max(self):
        return self.max
    
    def get_new_source(self):
        return self.new_source 
    
    def get_new_date(self):
        return self.new_date 

    #UPDATE
    def update_source(self):

        if self.new_source is not None:
            self.cursor.execute('''
            UPDATE denial
            SET source = ?
            WHERE id BETWEEN ? AND ?
        ''', (self.new_source, self.min, self.max))
            self.connection.commit()
        elif self.new_source == "" or self.new_source is None:
            self.source = self.get_source()
            for value in self.source.values():
                self.cursor.execute('''
                UPDATE denial
                SET source = ?
                WHERE id BETWEEN ? AND ?
            ''', (value, self.min, self.max))
    
    def update_date(self):
        error = False 
        if self.new_date is not None:

            self.denial_date = self.get_denial_date()
            min = self.min
            
            for idx, date_str in self.denial_date.items():
                if self.min <= idx <= self.max:
                    if date_str is not None:
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                            new_date_obj = self.new_date - date_obj
                            
                            if idx == min:
                                # Calculate the interval days
                                interval_days = new_date_obj.days
                                # Adjust the date by adding the interval days to the original date
                            new_date1 = date_obj + timedelta(days=interval_days)
                            new_date1_str = new_date1.strftime('%Y-%m-%d')
    
                            self.cursor.execute('''
                            UPDATE denial
                            SET denial_date = ?
                            WHERE id = ?
                        ''', (new_date1_str, idx))
                            
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    
                    else: 
                        min = min + 1
                        self.cursor.execute('''
                        UPDATE denial
                        SET denial_date = ?
                        WHERE id = ?
                    ''', (self.new_date.strftime('%Y-%m-%d'), idx))
                    
            self.connection.commit()
        return error
