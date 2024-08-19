import streamlit as st
from usage_class import usage_class
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
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            print(f"Connected to the existing database '{self.db_path}'.")
        self.create_tables()
    def create_tables(self):
        """Create tables if they do not exist."""
        # Example table creation
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS denial1 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                computer TEXT,
                product TEXT,
                created_on TEXT,
                updated_on TEXT,
                denial_count INTEGER,
                denial_date TEXT
            )
        ''')
        self.connection.commit()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        
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

                #new Addition  
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

    def set_source(self,source):

        self.source = source
    
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
        
        return self.denial_date

    def get_computer(self):
    
        return self.computer

    def get_source(self):

        return self.source
    
    def get_product(self):

        return self.product
    
    def get_created_on(self):
        return self.created_on
    
    def get_updated_on(self):

        return self.updated_on
    
    def get_total_denial_count(self):

        return self.total_denial_count
    
    def get_min(self):
        return self.min 
    
    def get_max(self):
        return self.max
    
    def get_new_source(self):
        return self.new_source 
    
    def get_new_date(self):
        return self.new_date 
