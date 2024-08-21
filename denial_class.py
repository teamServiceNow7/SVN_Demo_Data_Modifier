import streamlit as st
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
                computer_name TEXT,
                denial_date TEXT,
                denial_id TEXT,
                discovery_model TEXT,
                "group" TEXT,
                group_name TEXT,
                is_product_normalized TEXT,
                last_denial_time TEXT,
                license_server TEXT,
                license_server_name TEXT,
                license_type TEXT,
                license_type_name TEXT,
                norm_product TEXT,
                nom_product_name TEXT,
                norm_publisher TEXT,
                norm_publisher_name TEXT,
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
                user_name TEXT,
                version TEXT,
                workstation TEXT,
                workstation_name TEXT
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

        # Insert data into the table
        for elem in self.root.findall('.//samp_eng_app_denial'):
            data = []
            for col in columns:
                if col == 'id':
                    value = int(elem.find(col).text) if elem.find(col) is not None and elem.find(col).text.isdigit() else None
                elif col.endswith('_name'):
                    # Handle columns that map to display_value attributes
                    element_name = col.replace('_name', '')
                    element = elem.find(element_name)
                    value = element.get('display_value') if element is not None else ''
                else:
                    value = elem.find(col).text if elem.find(col) is not None else ''
                data.append(value)

            self.cursor.execute(insert_query, data)

        self.connection.commit()

    def delete_table(self):
        self.cursor.execute('DELETE FROM denial')

    def getall(self):
        self.cursor.execute('''SELECT * FROM denial''')
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        
    def update_denial(self):
        error = False
        value1 = None
        flag = 2
        col_idx = 0
        cols = st.columns(4)

        # Fetch data from the database
        rows = self.getall()
        print(f"Fetched rows: {rows}")

        data = []
        for idx, row in enumerate(rows, 1):
            # Print row to check its content
            print(f"Row {idx}: {row}")
            try:
                source = row[23]  # source
                computer = row[5]  # computer
                product = row[10]  # product
                sys_created_on = row[25]  # sys_created_on
                sys_updated_on = row[31]  # sys_updated_on
                total_denial_count = row[32]  # total_denial_count
                denial_date = row[6]  # denial_date

                # To change the source
                if self.new_source is not None:
                    self.set_new_source(self.new_source)
                    source = self.new_source
                else:
                    source = source

                # To change the denial_date
                if self.new_date:
                    if denial_date is not None:
                        try:
                            # Assuming usage_class.adjust_date_element() is available
                            value = usage_class.adjust_date_element(None, None, denial_date, self.new_date, idx, self.min, flag, value1)
                            value1 = value
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    else:
                        # Adjust the min_idle to get the next value if the first value is none
                        self.min += 1
                        # Replace all that have the none value into the inputted start date
                        denial_date = self.new_date.strftime('%Y-%m-%d')

                # New Addition (Dataframe)
                data.append({
                    'source': source, 'computer': computer, 'product': product,
                    'created_on': sys_created_on, 'updated_on': sys_updated_on,
                    'denial_count': total_denial_count, 'denial_date': denial_date
                })

                with cols[col_idx % 4].expander(f"#### Object {idx}", expanded=True):
                    st.markdown(f"""
                    **Denial Date**: {denial_date}  
                    **Computer Name**: {computer}  
                    **Product**: {product}  
                    **Source**: {source}  
                    **Created on**: {sys_created_on}  
                    **Updated on**: {sys_updated_on}  
                    **Total Denial Count**: {total_denial_count}  
                    """)
                col_idx += 1

            except IndexError as e:
                st.error(f"IndexError at row {idx}: {str(e)}")
                error = True
            except Exception as e:
                st.error(f"Unexpected error at row {idx}: {str(e)}")
                error = True

        df = pd.DataFrame(data)
        print(df)
        return error, self.tree 
    
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
