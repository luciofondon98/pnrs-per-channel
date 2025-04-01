import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import urllib3
from dotenv import load_dotenv
import os
from io import BytesIO

# Load environment variables
load_dotenv()

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_api_events_segment_data(start_date, end_date, api_key, secret_key, channel):
    """
    Realiza una llamada a la API de Amplitude para obtener datos de eventos
    """
    url = 'https://amplitude.com/api/2/events/segmentation'

    event_filter = {
        "event_type": "payment_confirmation_loaded",
        "filters": [
            {
                'group_type': 'User',
                'subprop_key': 'acce9394-0a0d-4285-95a8-c5c1678ddc86',
                'subprop_op': 'is',
                'subprop_value': [channel],
                'subprop_type': 'derivedV2',
                'subfilters': [],
            },
        ],
        "group_by": [{"type": "event", "value": "pnr"}]
    }
        
    params = {
        'e': json.dumps(event_filter),
        'm': 'totals',
        'start': str(start_date).replace('-',''),
        'end': str(end_date).replace('-',''),
        'limit': 20000,
        'i': 1
    }

    headers = {'Content-Type': 'application/json'}
    auth = (api_key, secret_key)

    response = requests.get(url, headers=headers, params=params, auth=auth, verify=False)
    return json.loads(response.text)

def process_data(data):
    pnrs = [pnr[1] for pnr in data['data']['seriesLabels']]
    transactions = [transaction[0] for transaction in data['data']['series']]
    payment_date = data['data']['xValues'][0]
    
    df = pd.DataFrame({
        'payment_date': payment_date,
        'pnr': pnrs,
        'transactions': transactions
    })
    return df

def generate_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]

def main():
    st.set_page_config(page_title="Amplitude Data Fetcher", layout="wide")
    st.title("Amplitude Data Fetcher")
    
    # Get API credentials from environment variables
    api_key = os.getenv('API_KEY')
    secret_key = os.getenv('SECRET_KEY')
    
    if not api_key or not secret_key:
        st.error("API credentials not found in .env file. Please make sure API_KEY and SECRET_KEY are set.")
        return

    # Main content
    st.header("Date Range Selection")
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Convert dates to string format
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    channels = [
        'Email', 'Paid Search', 'Affiliates', 'Metasearch', 'Direct',
        'Organic Search', 'Display', 'Web Push', 'Referral', 'Social'
    ]
    
    if st.button("Fetch Data"):
        with st.spinner("Fetching data from Amplitude..."):
            date_range = generate_date_range(start_date_str, end_date_str)
            all_data = []
            
            progress_bar = st.progress(0)
            total_steps = len(date_range) * len(channels)
            current_step = 0
            
            for date in date_range:
                for channel in channels:
                    try:
                        data = get_api_events_segment_data(date, date, api_key, secret_key, channel)
                        df = process_data(data)
                        df['channel'] = channel
                        all_data.append(df)
                        
                        current_step += 1
                        progress_bar.progress(current_step / total_steps)
                    except Exception as e:
                        st.error(f"Error fetching data for {channel} on {date}: {str(e)}")
            
            if all_data:
                final_df = pd.concat(all_data, ignore_index=True)
                
                # Display the data
                st.header("Data Preview")
                st.dataframe(final_df)
                
                # Export to Excel
                st.header("Export Data")
                # Create a BytesIO object to store the Excel file
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    final_df.to_excel(writer, index=False)
                
                # Get the value of the BytesIO buffer and write it to the download button
                excel_data = buffer.getvalue()
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=f"amplitude_data_{start_date_str}_{end_date_str}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No data was fetched. Please check your API credentials and try again.")

if __name__ == "__main__":
    main() 