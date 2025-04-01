# Amplitude Data Fetcher

This Streamlit application allows you to fetch data from Amplitude's API and export it to Excel format.

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Streamlit app:
```bash
streamlit run app.py
```

## Usage

1. Enter your Amplitude API credentials in the sidebar
2. Select the date range you want to fetch data for
3. Click the "Fetch Data" button
4. Wait for the data to be fetched (progress bar will show the status)
5. Once complete, you can:
   - View the data in the preview table
   - Download the data as an Excel file

## Features

- Date range selection
- Secure API credential input
- Progress tracking
- Data preview
- Excel export functionality
- Error handling for API calls 