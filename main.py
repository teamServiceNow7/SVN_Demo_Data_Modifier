import streamlit as st
import xml.etree.ElementTree as ET
import sqlite3
import time
import pandas as pd
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta
from usage_class import usage_class
from concurrent_class import concurrent_class
from denial_class import denial_class
sidebar_bg_img = """
    
    <style>
    #MainBg
    .st-emotion-cache-1r4qj8v {
    position: absolute;
    background: #FFFAFA;
    color: rgb(49, 51, 63);
    inset: 0px;
    color-scheme: light;
    overflow: hidden;
    }
    
    h1 {
    font-family: "Font Awesome 6 Pro", sans-serif;
    font-weight: 800;
    font-variant: small-caps;
    background: linear-gradient(to top, #032C41, #02506B);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    padding: 0rem 0px 1rem;
    margin: 0px;
    line-height: 1;
    }
    
    /*Image Title*/
    .st-emotion-cache-1v0mbdj {
    display: block;
    margin-left: auto;
    margin-right: auto;
    display: flex;
    flex-direction: column;
    -webkit-box-align: stretch;
    align-items: stretch;
    width: auto;
    -webkit-box-flex: 0;
    flex-grow: 0;
    margin-bottom: 1rem;
    margin-top: 0rem;
    }
    
    .st-emotion-cache-1jicfl2 {
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* header red #920113-red hex*/ 
    h2{
    background-color: #920113;
    color: white;
    font-variant-caps: all-small-caps;
    text-align: center;
    border-radius: 10px;
    }
    
    h2 {
    font-family: "Source Sans Pro", sans-serif;
    font-weight: 600;
    letter-spacing: -0.005em;
    padding: 0.25rem 0px;
    margin: 0px;
    line-height: 1.2;
    }
    
    h3{
    font-weight: bold;
    font-size: 20px;
    }
    
    /*side bar subhead*/
    .st-emotion-cache-1fnth58 p{
    font-weight: bold;
    font-size: 20px;   
    }

    h4{
    color: #920113;
    }
    .stProgress > div > div > div > div {
        background-color: #920113;
    }
    
    [data-testid= "stThumbValue"]{
    color: #920113;
    }
    /*Logo*/
    .st-emotion-cache-5drf04 {
    height: 7rem;
    max-width: 20rem;
    margin: 0.25rem 0.5rem 0.25rem 0px;
    z-index: 999990;
    }
    
    /*sidebar heading-demodata xml*/
    .st-emotion-cache-1gwvy71 {
    padding: 0px 1.5rem 6rem;
    }
    
    .st-emotion-cache-1gwvy71 h1 {
    font-family: "League Spartan", sans-serif;
    color: #ffffff;
    background-color: #032C41;
    font-size: 23px;
    }
    
     /*sidebar gap */
    .st-emotion-cache-1dfdf75 {
    width: 282px;
    position: relative;
    display: flex;
    flex: 0.5 0.5 0%;
    flex-direction: column;
    gap: 0.75rem;
    flex-wrap: nowrap;
    }
    
    /*date expander gap*/
    .st-emotion-cache-phzz4j {
    width: 248px;
    position: relative;
    /* display: flex; */
    flex: 0.5 0.5 0%;
    flex-direction: column;
    gap: 0.25rem;
    }
    
    .st-emotion-cache-1mi2ry5 {
    display: flex;
    -webkit-box-pack: justify;
    justify-content: space-between;
    -webkit-box-align: start;
    align-items: start;
    padding:  0.5rem 0.5rem 0.25rem ;
    }
    
    /*Sidebar Components*/
    .st-emotion-cache-ue6h4q {
    font-size: 14px;
    color: rgb(49, 51, 63);
    display: flex;
    visibility: visible;
    margin-bottom: 0.5rem;
    height: auto;
    min-height: 1.5rem;
    vertical-align: middle;
    flex-direction: row;
    -webkit-box-align: center;
    align-items: center;
    }
    
    [data-testid="stSidebar"]{
    background-color: #E6EDF1;    
    width: 20%;
    }
    
    [data-testid= "stHeader"]{
    background-color: #920113;
    color: #ffffff;
    padding: 1rem;
    }
    
    [data-testid= "stSidebarUserContent"]{
    background-color: #6d0b17;
    height: 1px;
    }
    
    [data-testid= "stSidebarHeader"]{
    background-color: #6d0b17;
    }
    
    /*new date value*/
    .st-emotion-cache-1gwvy71 h3 {
    font-size: 20px;
    font-weight: bold;
    }   

    
    .st-emotion-cache-1ag92y2{
    background-color: #E6EDF1; 
    }

    /*gap between buttons*/
    .st-emotion-cache-64tehz {
        width: 288px;
        position: relative;
        display: flex;
        flex: 1 1 0%;
        flex-direction: column;
        gap: 0.5rem;
    }

    /*sidebar subheader text*/
    .st-emotion-cache-1qy8wcg p {
        word-break: break-word;
        font-size: 20px;
        font-weight: bold;
    }

    
    div[data-testid="stExpander"] details summary p{
        font-size: 4rem;
    }
    
    /*for paragraph*/
    p, ol, ul, dl {
        font-size: 1rem;
        font-weight: 400;
    }

    div[data-testid="stMetricValue"] > div {
        color: #920113;
        font-size: 50px
    }

    /*expander margin*/
    .st-emotion-cache-1fnth58 {
        position: relative;
        display: flex;
        width: 100%;
        font-size: 14px;
        padding: 0px 1rem;
        list-style-type: none;
        background-color:#E6EDF1; 
    }
    </style>                 
            
"""
def upload_xml(db_path, xml_file_path):
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    
        # Create table if it does not exist
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS default_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                xml_files BLOB
            )
        ''')
    
        # Read XML file
        with open(xml_file_path, 'rb') as file:
            xml_data = file.read()
    
        # Insert XML data into the database
        cursor.execute(f''' SELECT COUNT(*) FROM default_files''')
        rows = cursor.fetchone()[0]

        if rows < 3:
            cursor.execute(f'''
                INSERT INTO default_files (xml_files) VALUES (?)
            ''', (xml_data,))
            # Commit and close the connection
            conn.commit()
            conn.close()
            print(f"XML file {xml_file_path} uploaded to database.")

def retrieve_xml(db_path, record_id, output_file_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
   
    try:
        # Query to fetch XML data
        cursor.execute(f'''
            SELECT xml_files FROM default_files WHERE id = ?
        ''', (record_id,))
       
        # Fetch the data
        xml_data = cursor.fetchone()[0]
 
        # Check if data was retrieved
        if xml_data:
            #Save XML data to a file
            with open(output_file_path, 'wb') as file:
                file.write(xml_data)
            print(f"XML data saved to {output_file_path}.")
            return xml_data
        else:
            print("No data found.")
    except sqlite3.Error as e:
        print(f"Error retrieving XML data: {e}")
    finally:
        # Close the connection
        conn.close()

# Example usage for uploading XML
db_path = 'xmlDB.db'

#Function for writing the XML file
def save_modified_xml(file_name, tree):
    modified_xml = BytesIO()
    tree.write(modified_xml, encoding='utf-8', xml_declaration=True)
    modified_xml.seek(0)
    return modified_xml

def time_to_decimal_hours(time_str):
    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    hours = dt.hour
    minutes = dt.minute
    decimal_hours = hours + minutes / 60      # Convert time to decimal hours
    return decimal_hours
    
#Main Function 
def main():
    # Initialize session state variables
    if 'previous_file_index' not in st.session_state:
        st.session_state.previous_file_index = None

    file_changed = False
    error = False
    def_file = False
    selected_file = None
    uploaded_files = None
      
    # Progress bar (if needed)
    st.image("XML_TitleHeader.png")
    placeholder = st.empty()
    placeholder1 = st.empty()
    placeholder2 = st.empty()
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()
    # Sidebar for file selection and source update
    st.sidebar.title("ServiceNow ENGINEERING DEMO DATA MODIFIER")
    st.sidebar.divider()
    st.sidebar.subheader("Choose file to modify")

    # Initialize session state variables if not already set
    if 'show_uploader' not in st.session_state:
        st.session_state.show_uploader = False  # Hide uploader initially
    if 'show_default' not in st.session_state:
        st.session_state.show_default = False
    if 'default_files_clicked' not in st.session_state:
        st.session_state.default_files_clicked = False
    if 'previous_file_index' not in st.session_state:
        st.session_state.previous_file_index = -1

    # Sidebar buttons
    upload_button = st.sidebar.button("Upload XML Files", use_container_width=True, type="primary")
    default_button = st.sidebar.button("Use Default Files", use_container_width=True)
    st.sidebar.divider()

    # Handle "Upload XML Files" button click
    if upload_button:
        st.session_state.show_uploader = True
        st.session_state.show_default = False
        st.session_state.default_files_clicked = False

    # Handle "Use Default Files" button click
    if default_button:
        st.session_state.show_uploader = False
        st.session_state.show_default = True
        st.session_state.default_files_clicked = True

    # Show file uploader or default files based on session state
    if st.session_state.show_uploader and not st.session_state.default_files_clicked:
        with st.sidebar.expander("#### UPLOAD FILES", expanded=True):
            uploaded_files = st.file_uploader("Choose XML files", accept_multiple_files=True, type=["xml"])

            if uploaded_files:
                file_names = [file.name for file in uploaded_files]
                selected_file_name = st.sidebar.selectbox("Select a file to focus on", file_names)

                for uploaded_file in uploaded_files:
                    if uploaded_file.name == selected_file_name:
                        selected_file = uploaded_file
                        break
                selected_file_index = file_names.index(selected_file_name)

                # Check if the selected file has changed
                if selected_file_index != st.session_state.previous_file_index or selected_file is None:
                    file_changed = True
                    st.session_state.previous_file_index = selected_file_index
                else:
                    file_changed = False

    if st.session_state.show_default:
        # Retrieve the default XML files for use
        record_id = 1
        output_file_path = 'default_denial.xml'
        default_denial = retrieve_xml(db_path, record_id, output_file_path)

        record_id = 2
        output_file_path = 'default_concurrent.xml'
        default_concurrent = retrieve_xml(db_path, record_id, output_file_path)

        record_id = 3
        output_file_path = 'default_usage.xml'
        default_usage = retrieve_xml(db_path, record_id, output_file_path)

        default_files = [default_denial, default_concurrent, default_usage]

        # Process the default files
        file_names = ['default_denial.xml', 'default_concurrent.xml', 'default_usage.xml']
        selected_file_name = st.sidebar.selectbox("Select a default file to focus on", file_names)

        if selected_file_name == file_names[0]:
            selected_file = default_files[0]
            file_name = 'samp_eng_app_denial.xml'
        elif selected_file_name == file_names[1]:
            selected_file = default_files[1]
            file_name = 'samp_eng_app_concurrent.xml'
        elif selected_file_name == file_names[2]:
            selected_file = default_files[2]
            file_name = 'samp_eng_app_usage_summary.xml'
        def_file = True

        selected_file_index = file_names.index(selected_file_name)
        # Check if the selected file has changed
        if selected_file_index != st.session_state.previous_file_index:
            file_changed = True
            st.session_state.previous_file_index = selected_file_index
        else:
            file_changed = False
            
    if selected_file:
        
        # Load and parse the XML file
        if uploaded_files:
            tree = ET.parse(selected_file)
            root = tree.getroot()
            file_name = selected_file.name
            # Remove the prefix, file extension, and underscores, then convert to proper case
            display_file_name = file_name.replace("samp_eng_app_", "").replace("_", " ").rsplit('.', 1)[0].title()
        else:
            tree = ET.ElementTree(ET.fromstring(selected_file))
            root = tree.getroot()
            
            display_file_name = selected_file_name.replace("_", " ").replace(".xml", " ").title()
        st.header(f"Update {display_file_name}")
        st.write(" ")
        elements = None
        usage = root.find('.//samp_eng_app_usage_summary[@action="INSERT_OR_UPDATE"]')
        concurrent = root.find('.//samp_eng_app_concurrent_usage[@action="INSERT_OR_UPDATE"]')
        denial = root.find('.//samp_eng_app_denial[@action="INSERT_OR_UPDATE"]')
        
        # Find all elements with the specified action attribute
        
        elements = root.findall(".//*[@action]")
            
        # Count the elements
        count = len(elements)
        min_range, max_range = st.sidebar.slider("Select Range", min_value=1, max_value=count, value=(1, count), key="select_range")
        # Fields that are always visible
        with st.sidebar.expander(f"#### Edit Source Value", expanded=True):
            st.markdown("")
            new_source = st.text_input("New Source Value", "")
        if new_source == "":
            new_source = None
        st.sidebar.subheader("New Date Value", "")
        # Determine the appropriate label [EDITED]
        if denial:
            label = "Update Denial Date"
        else:
            label = "Update Usage Date"
        # Display the date input with the corresponding label
        with st.sidebar.expander(f"#### {label}", expanded=True):
            st.markdown("")
            new_date = st.date_input("Enter Start Date", value=None)
        if usage:
            with st.sidebar.expander(f"#### Update Idle Duration"):
                st.markdown("")
                idle_dur_date = st.date_input("Enter Idle Duration (Date)", value=None)
                idle_dur_time = st.time_input("Enter Idle Duration (Time)", value=None, step=60)
                
            with st.sidebar.expander(f"#### Session Duration"):
                st.markdown("")
                session_dur_date = st.date_input("Enter Session Duration (Date)", value=None)
                session_dur_time = st.time_input("Enter Session Duration (Time)", value=None, step=60)
            # Condition to not update if there is one none in either idle_dur_date or idle_dur_time
            if ((idle_dur_date is not None) and (idle_dur_time is not None)):
                total_idle_dur = datetime.combine(idle_dur_date, idle_dur_time)
            else:
                total_idle_dur = None 
            # Condition to not update if there is one none in either session_dur_date or session_dur_time
            if ((session_dur_date is not None) and (session_dur_time is not None)):        
                total_session_dur = datetime.combine(session_dur_date, session_dur_time)
            else:
                total_session_dur = None
        update_button = st.sidebar.button("Update All Fields")
        #st.sidebar.write(" ")

        if usage:

            # Create an instance of the `usage_class`
            usg = usage_class(tree, root, min_range, max_range, db_path, new_source, new_date,
                              total_idle_dur, total_session_dur, file_changed, def_file)

            # Check if the 'update_button' is press
            if update_button:

                # If a new source is provided, update the usage source
                if new_source is not None:
                    usg.update_usage_source()
                # If a new date is provided, update the usage date
                if new_date is not None:
                    error = usg.update_usage_date()
                 # If a new total idle duration is provided, update the idle duration
                if total_idle_dur is not None:
                    usg.update_usage_idle_dur()
                 # If a new total idle duration is provided, update the sess duration
                if total_session_dur is not None:
                    usg.update_usage_sess_dur()
                # Parse the updated usage data and save the modified XML
                tree = usg.usage_parser()
                modified_xml = save_modified_xml(file_name, tree)
                # Provide a button in the sidebar to download the modified XML file
                st.sidebar.download_button(
                    label="Download Modified XML",
                    data=modified_xml,    
                    file_name=file_name,
                    mime='application/xml',
                    type="primary"
                )
                st.sidebar.write("  ")
                if error:
                    placeholder.error(":x: Not Updated!")
                else:
                    placeholder.success(":white_check_mark: All fields updated successfully!")

            # Display the usage information
            usg.disp_usage()

            #For Graphs of Usage Summary
            with placeholder1:
                 
                df = pd.DataFrame({
                    'usage_date': usg.get_usage_date(),
                    'total_sess_dur': usg.get_sess_dur(),
                    'norm_product': usg.get_product(),
                    'norm_publisher': usg.get_norm_publisher()
                })
            
                col1, col2= st.columns((2))
                df['usage_date'] = pd.to_datetime(df['usage_date'])

                #Getting the min and max date
                startDate = pd.to_datetime(df['usage_date']).min()
                endDate = pd.to_datetime(df['usage_date']).max()

                with col1:
                    date1 = pd.to_datetime(st.date_input(":date: Start Date", startDate))
                with col2:
                    date2 = pd.to_datetime(st.date_input(":date: End Date", endDate))
                    df = df[(df['usage_date'] >= date1) & (df['usage_date'] <= date2)].copy()

            with placeholder2:    
                col3, col4= st.columns([3, 1], gap="small")

                with col3:
                    containerA = st.container(border=True, height=400)
                    containerA.subheader("Sesion Duration over time")
                    datetime_strings = df['total_sess_dur']
                    decimal_hours_list = [time_to_decimal_hours(dt_str) for dt_str in datetime_strings]
                    
                    df['total_sess_dur'] = (decimal_hours_list)
                    df.set_index('usage_date', inplace=True)
                    df_daily = df.resample('D').sum()

                    containerA.line_chart(
                        df_daily,
                        y="total_sess_dur", 
                        x_label='Usage Date', 
                        y_label='Session Duration (Hours)', 
                        color='#920113', 
                        use_container_width=True,
                        height=320
                    )
                    
                    usage_count= pd.Series(df['total_sess_dur']).astype(int)
                   
                    with col4:
                        containerProducts = st.container(border=True, height=400)
                        containerProducts.subheader("Normalized Products")
                        dfProduct= df[['norm_product', 'norm_publisher']].drop_duplicates()
                        containerProducts.data_editor(
                        dfProduct,
                            column_config={
                                'norm_product': st.column_config.Column(
                                    "Product Name",
                                    help="**Product Feature**",
                                    width = "small",
                                    disabled=True
                                ),
                                'norm_publisher': st.column_config.Column(
                                    "Publisher Name",
                                    help="**Publisher**",
                                    width = "small",
                                    disabled=True
                                )                                 
                            },
                            hide_index=True,
                            use_container_width=True
                        )  

            usg.close()
            
        elif concurrent:
            # Create an instance of the `concurrent_class`
            conc = concurrent_class(tree, root, min_range, max_range, db_path, new_source, new_date, file_changed, def_file)

            # Check if the 'update_button' is press
            if update_button:
                # If a new source is provided, update the concurrent source
                if new_source is not None:
                    conc.update_concurrent_source()
                # If a new date is provided, update the concurrent date
                if new_date is not None:
                    error = conc.update_concurrent_date()
                # Parse the updated concurrent data and save the modified XML
                tree = conc.concurrent_parser()
                modified_xml = save_modified_xml(file_name, tree)
                # Provide a button in the sidebar to download the modified XML file
                st.sidebar.download_button(
                    label="Download Modified XML",
                    data=modified_xml,    
                    file_name=file_name,
                    mime='application/xml',
                    type="primary"
                )
                st.sidebar.write("  ")
                if error:
                    placeholder.error(":x: Not Updated!")
                else:
                    placeholder.success(":white_check_mark: All fields updated successfully!")
            # Display the concurrent information
            conc.disp_concurrent()

            #For Graphs of Concurrent Usage
            with placeholder1:
                
                df = pd.DataFrame({
                    'usage_date': conc.get_usage_date(),
                    'concurrent_usage': conc.get_concurrent_usage(),
                    'Product': conc.get_license_name()
                })

                #Dates Tab Graph
                col1, col2= st.columns((2))
                df['usage_date'] = pd.to_datetime(df['usage_date'])

                #Getting the min and max date
                startDate = pd.to_datetime(df['usage_date']).min()
                endDate = pd.to_datetime(df['usage_date']).max()

                with col1:
                    date1 = pd.to_datetime(st.date_input(":date: Start Date", startDate))
                with col2:
                    date2 = pd.to_datetime(st.date_input(":date: End Date", endDate))
                    df = df[(df['usage_date'] >= date1) & (df['usage_date'] <= date2)].copy()
                
            with placeholder2:
                containerA = st.container(border=True)
                containerA.subheader("Concurrent Usage over time")
                con_count= pd.Series(df['concurrent_usage'])
                df['concurrent_usage'] = con_count.astype(int)
                
                dateStr= pd.Series(df['usage_date'])
                df['usage_date'] = dateStr.astype(str)

                containerA.bar_chart(df,
                    x='usage_date',
                    y='concurrent_usage', 
                    x_label='Usage Date', 
                    y_label='Concurrent Usage', 
                    color='Product', 
                    stack= False,
                    use_container_width=True
                )

            conc.close()
    
        elif denial:
            # Create an instance of the `denial_class`
            deny = denial_class(tree, root, min_range, max_range, db_path, new_source, new_date, file_changed, def_file)
            # Check if the 'update_button' is press
            if update_button:
                # If a new source is provided, update the denial source
                if new_source is not None:
                    deny.update_denial_source()
                # If a new date is provided, update the denial date
                if new_date is not None:
                    error = deny.update_denial_date()
                # Parse the updated usage data and save the modified XML
                tree = deny.denial_parser()
                modified_xml = save_modified_xml(file_name, tree)
                # Provide a button in the sidebar to download the modified XML file
                st.sidebar.download_button(
                    label="Download Modified XML",
                    data=modified_xml,    
                    file_name=file_name,
                    mime='application/xml',
                    type="primary"
                )
                st.sidebar.write("  ")
                if error:
                    placeholder.error(":x: Not Updated!")
                else:
                    placeholder.success(":white_check_mark: All fields updated successfully!")
            # Display the denial information       
            deny.disp_denial()
            
            #Code for Graphs of Denial
            with placeholder1:
 
                df = pd.DataFrame({
                    'denial_date': deny.get_denial_date(),
                    'denial_count': deny.get_total_denial_count(),
                    'computer': deny.get_computer()
                })

                # Dates Tab Graph
                col1, col2 = st.columns((2))
                
                df['denial_date'] = pd.to_datetime(df['denial_date'])
                # Getting the min and max date
                startDate = pd.to_datetime(df['denial_date']).min()
                endDate = pd.to_datetime(df['denial_date']).max()
                
                with col1:
                    date1 = pd.to_datetime(st.date_input(":date: Start Date", startDate))
                with col2:
                    date2 = pd.to_datetime(st.date_input(":date: End Date", endDate))
                    df = df[(df['denial_date'] >= date1) & (df['denial_date'] <= date2)].copy()
                    
            with placeholder2:
                col3, col4 = st.columns([3, 1], gap="small")
                
                with col3:
                    container = st.container(border=True)
                    container.subheader("Denial Count over time")
                    den_count = pd.Series(df['denial_count'])
                    df['denial_count'] = den_count.astype(int)
                    container.bar_chart(df, x='denial_date', 
                                        y='denial_count', 
                                        x_label='Denial Date', 
                                        y_label='Denial Count', 
                                        use_container_width=True, 
                                        color="#920113")
                     
                with col4:
                    container2 = st.container(border=True, height=150)
                    array = pd.Series(df['denial_count'])
                    array_int = array.astype(int).sum()
                    container2.metric(label="Total Denial Count", value= array_int)
                    #container2.subheader("Total Denial Count")
                    #container2.header(array_int)

                with col4:
                    dfUser = pd.DataFrame({
                    'Computer': df['computer'],
                    'Denial Count': df['denial_count']
                    })

                    # Convert 'Denial Count' from string to numeric, coercing errors to NaN
                    dfUser['Denial Count'] = pd.to_numeric(dfUser['Denial Count'], errors='coerce')

                    # Group by 'Computer' and sum 'Denial Count'
                    unique_user_df = dfUser.groupby('Computer', as_index=False)['Denial Count'].sum()

                    # Optionally, rename columns
                    unique_user_df.columns = ['Computer', 'Total Denial Count']

                    container3 = st.container(border=True, height=270)
                    container3.subheader("Denials per User")
                    container3.data_editor(
                       unique_user_df,
                        column_config={
                            'Total Denial Count': st.column_config.Column(
                                "Denial Count",
                                help="User **Denial Count**",
                                width = "small",
                                disabled=True
                            ),
                            "Computer": st.column_config.TextColumn(
                                "PC Name",
                                help="User **PC Name**",
                                default="st.",
                                width = "medium",
                                disabled=True
                            ),
                        },
                        hide_index=True,
                        use_container_width=True
                    )             
            deny.close()
            
        else:
            st.write(f"Unknown file type: {file_name}")
            return
if __name__ == "__main__":
    DDMIcon= Image.open("DDM_Icon.ico")
    st.set_page_config(
        page_title="SVN Demo Data Modifier",
        layout="wide",
        page_icon=DDMIcon
        )
    
    st.markdown(sidebar_bg_img, unsafe_allow_html=True)
    st.logo("logoSN.png")
    main()
