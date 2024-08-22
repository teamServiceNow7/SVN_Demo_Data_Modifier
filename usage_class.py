import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os

#class for usage 
class usage_class:

    def __init__(self, tree,root , min, max,db_path,new_source,new_date,total_idle_dur, total_session_dur):

        self.tree = tree
        self.root = root
        self.product = None
        self.normalized_name = None
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
        self.insert_data()

    def create_tables(self):
        """Create tables if they do not exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                norm_product TEXT,
                norm_product_name TEXT,
                norm_publisher TEXT,
                norm_publisher_name TEXT,
                reporting_version TEXT,
                source TEXT,
                sys_created_by TEXT,
                sys_created_on TEXT,
                sys_domain TEXT,
                sys_domain_path TEXT,
                sys_id TEXT,
                sys_mod_count INTEGER,
                sys_updated_by TEXT,
                sys_updated_on TEXT,
                total_idle_dur TEXT,
                total_sess_dur TEXT,
                usage_date TEXT,
                user TEXT,
                user_name TEXT
            )
        ''')
        self.connection.commit()

    def insert_data(self):
        """Insert data from XML into the 'usage_summary' table."""
        self.cursor.execute("PRAGMA table_info(usage_summary)")
        columns = [row[1] for row in self.cursor.fetchall()]
        columns_str = ', '.join([f'"{col}"' for col in columns])
        placeholders = ', '.join(['?'] * len(columns))
        insert_query = f'INSERT INTO usage_summary ({columns_str}) VALUES ({placeholders})'

        # Insert data into the table
        for elem in self.root.findall('.//samp_eng_app_usage_summary'):
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
                    if col == 'sys_mod_count' and value.isdigit():
                        value = int(value)
                        
                data.append(value)

            self.cursor.execute(insert_query, data)

        self.connection.commit()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        

    #Function to adjust date_element
    def adjust_date_element(usage_date_elem,concurrent_date_elem,denial_date_elem, new_date, idx, min,flag,value1):
        
        # Parse the date from the appropriate element's text based on the 'flag' flag
        if (flag == 0):
            date_obj = datetime.strptime(usage_date_elem.text, '%Y-%m-%d')
        elif (flag == 1):
            date_obj = datetime.strptime(concurrent_date_elem.text, '%Y-%m-%d')
        elif (flag == 2):
            date_obj = datetime.strptime(denial_date_elem.text, '%Y-%m-%d')
        
        # Calculate the difference in days between new_date and the parsed date
        new_date_obj = new_date - date_obj.date()
        
        # Adjust the date if the index matches the minimum value
        if idx == min:
            #get the days of the interval
            value1 = new_date_obj.days
            # Set min_value to -1 to prevent further changes
            min = -1  
        # Adjust the date by adding the interval days to the original date
        new_date1 = date_obj + timedelta(days=value1)
        
        # Update the text of the appropriate date element with the new formatted date
        if (flag == 0):
            usage_date_elem.text = new_date1.strftime('%Y-%m-%d')
        elif (flag == 1):
            concurrent_date_elem.text = new_date1.strftime('%Y-%m-%d')
        elif (flag == 2):
            denial_date_elem.text = new_date1.strftime('%Y-%m-%d')

        #Return the value to retain the increment date
        return value1
    
    #function to adjust session and idle date
    def adjust_session_idle(idle_date_elem,session_date_elem,total_dur, idx, min,adjust,value1):
        
        # Parse the date from the appropriate element's text based on the 'adjust' flag
        if (adjust == 0):
            date_obj = datetime.strptime(idle_date_elem.text, '%Y-%m-%d %H:%M:%S')
        elif (adjust == 1):
            date_obj = datetime.strptime(session_date_elem.text, '%Y-%m-%d %H:%M:%S')
        
        # Calculate the new date by subtracting the parsed date from the total duration
        new_date_obj = total_dur - date_obj
        
        # Adjust the date if the index matches the minimum value
        if idx == min:
            # Convert the difference to minutes and update 'value1'
            value1 = new_date_obj.total_seconds() / 60
            # Set min_value to -1 to prevent further changes
            min = -1  
        # Calculate the new date by adding 'value1' minutes to the original date
        new_date1 = date_obj + timedelta(minutes=value1)
        
        # Update the text of the appropriate date element with the new formatted date
        if (adjust == 0):
            idle_date_elem.text = new_date1.strftime('%Y-%m-%d %H:%M:%S')
        elif (adjust == 1):
            session_date_elem.text = new_date1.strftime('%Y-%m-%d %H:%M:%S')
        #Return the value to retain the increment date
        return value1
    
    def update_usage(self):

        st.write("  ")
        cols = st.columns(4)  # Adjust the number of columns as needed
        # Initializion of values
        error = False
        col_idx = 0
        usage_value = 0 
        increment_date_idle =  0
        increment_date_sess =  0
        flag = 0  
        min_usage = self.min
        min_sess = self.min
        min_idle = self.min

        for idx, elem in enumerate(self.root.findall('.//samp_eng_app_usage_summary'), 1):
            #condition for the slider
            if (self.min <= idx <= self.max):
                #To change the source
                if self.new_source:
                    source_elem = elem.find('source')
                    if source_elem is not None:
                        source_elem.text = self.new_source
                #To change the usage_date in usage
                if self.new_date:
                    usage_date_elem = elem.find('usage_date')
                    #condition if the usage_date_elem.text have a value
                    if usage_date_elem is not None and usage_date_elem.text is not None:
                        try:
                            #calling the function to adjust the usage date
                            value = usage_class.adjust_date_element(usage_date_elem, None, None, self.new_date, idx, min_usage,flag,usage_value)
                            #storing the increment date value to use to other iterations
                            usage_value = value
                        #catching the errors (this will print if there are wrong format in date and if it have date calculation overflow)
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                        except OverflowError:
                            st.error(f"Date calculation overflow at index {idx}. Original idle duration: {usage_date_elem.text}")
                            error = True
                    else:
                        #adjusting the min_usage to get the next value if the first value is none
                        min_usage = min_usage+1
                        #replacing all that have the none value into the inputted start date
                        usage_date_elem.text = self.new_date.strftime('%Y-%m-%d')

                #To change the total_idle_dur in usage
                if self.total_idle_dur:
                    idle_date_elem = elem.find('total_idle_dur')
                    #condition if the idle_date_elem.text have a value
                    if idle_date_elem is not None and idle_date_elem.text is not None:
                        try:
                            #declaring of adjust variable to use in the function
                            adjust = 0
                            #calling the function to adjust idle_date
                            new_adjust_idle = usage_class.adjust_session_idle(idle_date_elem,None,self.total_idle_dur, idx, min_idle,adjust,increment_date_idle)
                            #storing the increment date value to use to other iterations
                            increment_date_idle = new_adjust_idle
                        #catching the errors (this will print if there are wrong format in date and if it have date calculation overflow)
                        except OverflowError:
                            st.error(f"Date calculation overflow at index {idx}. Original idle duration: {idle_date_elem.text}")
                            error = True
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    else:
                        #adjusting the min_idle to get the next value if the first value is none
                        min_idle = min_idle+1
                        #replacing all that have the none value into the inputted start date
                        idle_date_elem.text = self.total_idle_dur.strftime('%Y-%m-%d %H:%M:%S')

                #To change the total_session_dur in usage
                if self.total_session_dur:
                    session_date_elem = elem.find('total_sess_dur')
                    #condition if the session_date_elem.text have a value
                    if session_date_elem is not None and session_date_elem.text is not None:
                        try:
                            #declaring of adjust variable to use in the function
                            adjust = 1
                            #calling the function to adjust session_date
                            new_adjust_sess = usage_class.adjust_session_idle(None,session_date_elem,self.total_session_dur, idx, min_sess,adjust,increment_date_sess)
                            #storing the increment date value to use to other iterations
                            increment_date_sess = new_adjust_sess
                        #catching the errors (this will print if there are wrong format in date and if it have date calculation overflow)
                        except OverflowError:
                            st.error(f"Date calculation overflow at index {idx}. Original idle duration: {session_date_elem.text}")
                            error = True
                        except ValueError as e:
                            st.error(f"Error parsing date at index {idx}: time data '01-01-2024' does not match format YYYY-MM-DD")
                            error = True
                    else:
                        #adjusting the min_idle to get the next value if the first value is none
                        min_sess = min_sess+1
                        #replacing all that have the none value into the inputted start date
                        session_date_elem.text = self.total_session_dur.strftime('%Y-%m-%d %H:%M:%S')
            
                with cols[col_idx % 4].expander(f"#### Object {idx}", expanded=True):
                    st.markdown(f"""
                    **Product**: {elem.find('norm_product').get('display_value') if elem.find('norm_product') is not None else 'N/A'}  
                    **Source**: {elem.find('source').text if elem.find('source') is not None else 'N/A'}  
                    **Created on**: {elem.find('sys_created_on').text if elem.find('sys_created_on') is not None else 'N/A'}  
                    **Updated on**: {elem.find('sys_updated_on').text if elem.find('sys_updated_on') is not None else 'N/A'}  
                    **Idle Duration**: {elem.find('total_idle_dur').text if elem.find('total_idle_dur') is not None else 'N/A'}  
                    **Session Duration**: {elem.find('total_sess_dur').text if elem.find('total_sess_dur') is not None else 'N/A'}  
                    **Usage Date**: {elem.find('usage_date').text if elem.find('usage_date') is not None else 'N/A'}  
                    """)
                col_idx += 1

        return error, self.tree
    
    #SETTERS
    def set_product(self, product):
        self.product = product
    
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
        return self.product 

    def get_source(self):
        return self.source 
    
    def get_created_on(self):
        return self.created_on 
    
    def get_updated_on(self):
        return self.updated_on
    
    def get_idle_dur(self):
        return self.idle_dur
    
    def get_sess_dur(self):
        return self.sess_dur 

    def get_usage_date(self):
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
    
