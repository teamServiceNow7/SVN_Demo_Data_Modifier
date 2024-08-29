import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os

#class for usage 
class usage_class:

    def __init__(self, tree,root, min, max, db_path, new_source, new_date, total_idle_dur, total_session_dur, file_changed, def_file):

        self.tree = tree
        self.root = root
        self.product = None
        self.norm_publisher = None
        self.source = None
        self.created_on = None
        self.updated_on = None
        self.idle_dur = None
        self.sess_dur = None
        self.usage_date = None
        self.min = min
        self.max = max
        self.new_source = new_source
        self.new_date = new_date
        self.total_idle_dur = total_idle_dur
        self.total_session_dur = total_session_dur
        self.file_changed = file_changed
        self.def_file = def_file
        self.db_path = db_path

        if self.def_file is True:
            self.table_name = "default_usage"
        else:
            self.table_name = "usage_summary"
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
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT,
                norm_publisher TEXT,
                source TEXT,
                sys_created_on TEXT,
                sys_updated_on TEXT,
                idle_dur TEXT,
                sess_dur TEXT,
                usage_date TEXT
            )
        ''')
        self.connection.commit()

    def clear_table(self):
        self.cursor.execute(f'DROP TABLE IF EXISTS {self.table_name}')
        self.create_tables()
        self.cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{self.table_name}"')
        self.insert_data()
        
    def insert_data(self):
        self.cursor.execute(f'SELECT COUNT(*) FROM {self.table_name}')
        rows = self.cursor.fetchone()[0]
        # Insert data into the table
        if rows == 0:
            for elem in self.root.findall('.//samp_eng_app_usage_summary'):
                product = elem.find('norm_product').get('display_value')
                norm_publisher = elem.find('norm_publisher').get('display_value')
                source = elem.find('source').text
                sys_created_on = elem.find('sys_created_on').text
                sys_updated_on = elem.find('sys_updated_on').text
                idle_dur = elem.find('total_idle_dur').text
                sess_dur = elem.find('total_sess_dur').text
                usage_date = elem.find('usage_date').text

                self.cursor.execute(f'''
                                    INSERT INTO {self.table_name}(product, norm_publisher, source, sys_created_on, sys_updated_on, idle_dur, sess_dur, usage_date)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (product, norm_publisher, source, sys_created_on, sys_updated_on, idle_dur, sess_dur, usage_date))
        self.connection.commit()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        
    #SETTERS
    def set_product(self, product):
        self.product = product

    def set_norm_publisher(self, norm_publisher):
        self.norm_publisher = norm_publisher
    
    def set_source(self,source):
        self.source = source
    
    def set_created_on(self,created_on):
        self.created_on = created_on
    
    def set_updated_on(self,updated_on):
        self.updated_on = updated_on
    
    def set_idle_dur(self,idle_dur):
        self.idle_dur = idle_dur
    
    def set_sess_dur(self, sess_dur):
        self.sess_dur = sess_dur

    def set_usage_date(self, usage_date):
        self.usage_date = usage_date
    
    def set_tree(self,tree):
        self.tree = tree
    
    def set_root(self,root):
        self.root = root
    
    def set_min(self, min):
        self.min = min
    
    def set_max(self,max):
        self.max = max
    
    def set_new_source(self,new_source):
        self.new_source = new_source
    
    def set_new_date(self,new_date):
        self.new_date = new_date
    
    def set_total_idle_dur(self,total_idle_dur):
        self.total_idle_dur = total_idle_dur

    def set_total_session_dur(self,total_session_dur):
        self.total_session_dur = total_session_dur
    
    #GETTERS
    def get_product(self):

        self.cursor.execute(f'''
        SELECT id, product FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.product = {row[0]: row[1] for row in rows}

        return self.product
    
    def get_norm_publisher(self):

        self.cursor.execute(f'''
        SELECT id, norm_publisher FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.norm_publisher = {row[0]: row[1] for row in rows}

        return self.norm_publisher

    def get_source(self):

        self.cursor.execute(f'''
        SELECT id, source FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.source = {row[0]: row[1] for row in rows}

        return self.source 
    
    def get_created_on(self):
        self.cursor.execute(f'''
        SELECT id, sys_created_on FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.created_on = {row[0]: row[1] for row in rows}
        return self.created_on 
    
    def get_updated_on(self):

        self.cursor.execute(f'''
        SELECT id, sys_updated_on FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.updated_on = {row[0]: row[1] for row in rows}
        return self.updated_on
    
    def get_idle_dur(self):
        self.cursor.execute(f'''
        SELECT id, idle_dur FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.idle_dur = {row[0]: row[1] for row in rows}
        return self.idle_dur
    
    def get_sess_dur(self):

        self.cursor.execute(f'''
        SELECT id, sess_dur FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.sess_dur = {row[0]: row[1] for row in rows}
        return self.sess_dur 
    
    def get_usage_date(self):
        self.cursor.execute(f'''
        SELECT id, usage_date FROM {self.table_name}
        WHERE id BETWEEN ? AND ?
    ''', (self.min, self.max))
        
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()

        # Extract the single column from the rows and store it in self.computer      
        self.usage_date = {row[0]: row[1] for row in rows}
        return self.usage_date
    
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
    
    def get_total_idle_dur(self):
        return self.total_idle_dur 

    def get_total_session_dur(self):
        return self.total_session_dur

    def update_usage_source(self):

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
    
    def update_usage_date(self):
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
    
                            self.cursor.execute(f'''
                            UPDATE {self.table_name}
                            SET usage_date = ?
                            WHERE id = ?
                        ''', (new_date1_str, idx))
                            
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    
                    else: 
                        min = min + 1
                        self.cursor.execute(f'''
                        UPDATE {self.table_name}
                        SET usage_date = ?
                        WHERE id = ?
                    ''', (self.new_date.strftime('%Y-%m-%d'), idx))
                    
            self.connection.commit()
        return error
    
    def update_usage_idle_dur(self):

        error = False 
        if self.total_idle_dur is not None:

            self.idle_dur = self.get_idle_dur()
            min = self.min
            
            for idx, date_str in self.idle_dur.items():
                if self.min <= idx <= self.max:
                    if date_str is not None:
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

                            new_date_obj = self.total_idle_dur - date_obj
                            
                            if idx == min:
                                # Calculate the interval days
                                interval_days = new_date_obj.total_seconds() / 60
                                min = -1
                                # Adjust the date by adding the interval days to the original date
                            new_date1 = date_obj + timedelta(minutes = interval_days)
                            new_date1_str = new_date1.strftime('%Y-%m-%d %H:%M:%S')
    
                            self.cursor.execute(f'''
                            UPDATE {self.table_name}
                            SET idle_dur = ?
                            WHERE id = ?
                        ''', (new_date1_str, idx))
                            
                        #catching the errors (this will print if there are wrong format in date and if it have date calculation overflow)
                        except OverflowError:
                            st.error(f"Date calculation overflow at index {idx}. Original idle duration: {date_str}")
                            error = True
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    
                    else: 
                        min = min + 1
                        self.cursor.execute(f'''
                        UPDATE {self.table_name}
                        SET total_idle_dur = ?
                        WHERE id = ?
                    ''', (self.total_idle_dur.strftime('%Y-%m-%d %H:%M:%S'), idx))
                    
            self.connection.commit()
        return error
    
    def update_usage_sess_dur(self):
        error = False 
        if self.total_session_dur is not None:

            self.sess_dur = self.get_sess_dur()
            min = self.min
            
            for idx, date_str in self.sess_dur.items():
                if self.min <= idx <= self.max:
                    if date_str is not None:
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

                            new_date_obj = self.total_session_dur - date_obj
                            
                            if idx == min:
                                # Calculate the interval days
                                interval_days = new_date_obj.total_seconds() / 60
                                min = -1
                                # Adjust the date by adding the interval days to the original date
                            new_date1 = date_obj + timedelta(minutes = interval_days)
                            new_date1_str = new_date1.strftime('%Y-%m-%d %H:%M:%S')
    
                            self.cursor.execute(f'''
                            UPDATE {self.table_name}
                            SET sess_dur = ?
                            WHERE id = ?
                        ''', (new_date1_str, idx))
                            
                        #catching the errors (this will print if there are wrong format in date and if it have date calculation overflow)
                        except OverflowError:
                            st.error(f"Date calculation overflow at index {idx}. Original idle duration: {date_str}")
                            error = True
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    
                    else: 
                        min = min + 1
                        self.cursor.execute(f'''
                        UPDATE {self.table_name}
                        SET sess_dur = ?
                        WHERE id = ?
                    ''', (self.total_session_dur.strftime('%Y-%m-%d %H:%M:%S'), idx))
                    
            self.connection.commit()
        return error

    def disp_usage(self):

        col_idx = 0
        cols = st.columns(4)
        self.cursor.execute(f'''SELECT COUNT(*) FROM {self.table_name}''')
        rows = self.cursor.fetchone()[0]

        product = self.get_product()
        norm_publisher = self.get_norm_publisher()
        source = self.get_source()
        sys_created_on = self.get_created_on()
        sys_updated_on = self.get_updated_on()
        idle_dur = self.get_idle_dur()
        sess_dur = self.get_sess_dur()
        usage_date = self.get_usage_date()
    
        for idx in range(0,rows):
            
            display_idx = idx + 1

            if self.min <= display_idx <= self.max:
                
                with cols[col_idx % 4].expander(f"#### Object {display_idx}", expanded=True):
                    st.markdown(f"""
                    **Product**: {product[display_idx]}  
                    **Publisher**: {norm_publisher[display_idx]}          
                    **Source**: {source[display_idx]}  
                    **Created on**: {sys_created_on[display_idx]}  
                    **Updated on**: {sys_updated_on[display_idx]}  
                    **Idle Duration**: {idle_dur[display_idx]}  
                    **Session Duration**: {sess_dur[display_idx]}  
                    **Usage Date**: {usage_date[display_idx]}   
                    """)

                col_idx += 1

    def usage_parser(self):

        self.cursor.execute(f'''SELECT id, source FROM {self.table_name}''',)
        # Fetch all rows from the executed query
        rows = self.cursor.fetchall()
        # Extract the single column from the rows and store it in self.source        
        new_source = {row[0]: row[1] for row in rows}

        self.cursor.execute(f'''SELECT id, usage_date FROM {self.table_name}''',)
        rows1 = self.cursor.fetchall()
        new_date = {row[0]: row[1] for row in rows1}

        self.cursor.execute(f'''SELECT id, idle_dur FROM {self.table_name}''',)
        rows2 = self.cursor.fetchall()
        new_idle_dur = {row[0]: row[1] for row in rows2}

        self.cursor.execute(f'''SELECT id, sess_dur FROM {self.table_name}''',)
        rows3 = self.cursor.fetchall()
        new_sess_dur = {row[0]: row[1] for row in rows3}


        for idx, elem in enumerate(self.root.findall('.//samp_eng_app_usage_summary'), 1):

            source = elem.find('source')
            source.text = new_source[idx]
            usage_date = elem.find('usage_date')
            usage_date.text = new_date[idx]
            idle_dur = elem.find('total_idle_dur')
            idle_dur.text = new_idle_dur[idx]
            sess_dur = elem.find('total_sess_dur')
            sess_dur.text = new_sess_dur[idx]
    
        return self.tree
        
    def test(self):
        self.cursor.execute('''SELECT * FROM usage_summary''')
        result = self.cursor.fetchall()
        return result
