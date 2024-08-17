import streamlit as st
from usage_class import usage_class

#class for concurrent
class concurrent_class:

    def __init__(self):

        self.tree = None
        self.root = None
        self.min = None
        self.max = None
        self.new_source = None
        self.new_date = None
        self.license_name = None
        self.source = None
        self.usage_date = None
        self.created_on = None
        self.updated_on = None
    
    def update_concurrent(self):
    
        st.write("  ")
        cols = st.columns(4)  # Adjust the number of columns as needed
        col_idx = 0
        flag = 1
        value1 = 0
        error = False
 
        for idx, elem in enumerate(self.root.findall('.//samp_eng_app_concurrent_usage'), 1):
            #condition for the slider
            if (self.min <= idx <= self.max):
                #to change the source
                if self.new_source:
                    source_elem = elem.find('source')
                    if source_elem is not None:
                        source_elem.text = self.new_source
                #to change the usage_date in concurrent
                if self.new_date:
                    concurrent_date_elem = elem.find('usage_date')
                    #condition if the concurrent_date_elem.text have a value
                    if concurrent_date_elem is not None and concurrent_date_elem.text is not None:
                        try:
                            #calling the function to adjust the usage_date in concurrent
                            value = usage_class.adjust_date_element(None,concurrent_date_elem,None, self.new_date, idx, self.min,flag,value1)
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
                        concurrent_date_elem.text = self.new_date.strftime('%Y-%m-%d')
            
                with cols[col_idx % 4].expander(f"#### Object {idx}", expanded=True):
                    st.markdown(f"""
                    **License Name**: {elem.find('license').get('display_value') if elem.find('license') is not None else 'N/A'}  
                    **Source**: {elem.find('source').text if elem.find('source') is not None else 'N/A'}  
                    **Usage Date**: {elem.find('usage_date').text if elem.find('usage_date') is not None else 'N/A'}  
                    **Created on**: {elem.find('sys_created_on').text if elem.find('sys_created_on') is not None else 'N/A'}  
                    **Updated on**: {elem.find('sys_updated_on').text if elem.find('sys_updated_on') is not None else 'N/A'}  
                    """)
                col_idx += 1
    
        return error, self.tree
       
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

    def get_License_Name(self):
        return self.license_name
    
    def get_source(self):
        return self.source

    def get_usage_date(self):
        return self.usage_date 

    def get_created_on(self):
        return self.created_on 
    
    def get_updated_on(self):
        return self.updated_on 
    