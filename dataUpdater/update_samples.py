import paramiko
from scp import SCPClient
import sys
import os
import glob
import requests
import pandas as pd
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta
from django.conf import settings
from dataUpdater import dataFetch
from requests.exceptions import RequestException
from sample_volumes.models import Sample_Volumes, Facility, SampleType, DataUpdate


# function to download the csv file from click ussd dashboard

VALID_SAMPLE_CODES = [1, 2, 3, 4, 6]


def download_csv():

    # dashboard url
    url = "http://206.225.84.201/riders_test/sample_collection_export.php"

    # headers to get for authentication
    headers = CaseInsensitiveDict()
    headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    headers["Accept-Language"] = "en-GB,en-US;q=0.9,en;q=0.8"
    headers["Cache-Control"] = "max-age=0"
    headers["Connection"] = "keep-alive"
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Cookie"] = "searchPanel=%7B%22panelState_sample_collection_1%22%3A%7B%22srchPanelOpen%22%3Afalse%2C%22srchCtrlComboOpen%22%3Afalse%2C%22srchWinOpen%22%3Afalse%2C%22openFilters%22%3A%5B%5D%7D%7D; username=riders; password=health; s1574928373=d5b799606ae8c3085a479423a5b14748"
    headers["Origin"] = "http://206.225.84.201"
    headers["Referer"] = "http://206.225.84.201/riders_test/sample_collection_export.php"
    headers["Sec-GPC"] = "1"
    headers["Upgrade-Insecure-Requests"] = "1"
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"

    # parameter for getting all the samples
    data = "type=csv&records=all&rndVal=0.28999320348498614"

    try:
        # Pull the data
        print("Downloading reported volumes...")
        resp = requests.post(url, headers=headers, data=data)

        # Check if the request was successful
        if resp.status_code == 200:
            # Timestamp and file name
            now = datetime.now()
            date_time_stamp = now.strftime("%Y%m%d%H%M%S")
            file_path = f"{settings.BASE_DIR}{os.sep}reported_volumes{os.sep}sample_collection-{date_time_stamp}.csv"

            # Save the file
            with open(file_path, 'wb') as f:
                f.write(resp.content)

            print("Download completed successfully")
            return file_path  # Return the path to the saved file

        else:
            print(
                f"Download failed. Server responded with status code {resp.status_code}")
            return "Download failed: Server error"

    except RequestException as e:
        # Handle any error during the download request
        print(f"Download failed due to error: {e}")
        return f"Download failed: {str(e)}"

# function to process the data


def process_csv(file_path):
    try:
        # Read in the file
        with open(file_path, 'r') as file:
            filedata = file.read()

        # Replace unwanted strings
        filedata = filedata.replace(
            '* Closing connection 0\n', '').replace('* Closing connection 0', '')

        # Write the cleaned data back
        with open(file_path, 'w') as file:
            file.write(filedata)

    except Exception as e:
        return f"Error processing file: {e}"

    try:
        # Load CSV into DataFrame
        df = pd.read_csv(file_path)
        print("Success fetching CSV data.")
    except Exception as e:
        return f"Error reading CSV file: {e}"

    try:
        # Ensure 'date' column exists
        if 'date' not in df.columns:
            return "Error: 'date' column not found in CSV."

        # Convert 'date' column to datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Define the date range for the past 3 days (including today)
        today = datetime.now()
        three_days_ago = today - timedelta(days=2)

        # Filter data
        filtered_df = df[df['date'].between(three_days_ago, today)]

        # Convert 'sample' column to integer and filter valid sample codes
        df['sample'] = pd.to_numeric(df['sample'], errors='coerce').astype(
            'Int64')  # Handle NaN values properly
        df = df[df['sample'].isin(VALID_SAMPLE_CODES)]

        return filtered_df

    except Exception as e:
        return f"Error filtering data: {e}"

# helper function to log the rejections


def log_rejection(log_file, session_id, reason):
    """ Helper function to log rejected samples """
    log_file.write(f'{session_id},{reason}\n')

# function to save the processed daa to the database


def save_to_database(cleaned_data):
    """
    Processes the cleaned data and saves valid sample volumes to the database.
    Logs rejections with reasons.
    """

    # Initialize tracking dictionaries
    sample_volumes_added = {'total_added': 0, 'session_ids': []}
    sample_volumes_rejected = {'total_rejected': 0,
                               'session_ids': [], 'reason_for_rejection': []}

    # Setup logging directory and file
    log_dir = os.path.join(settings.BASE_DIR, "logs")
    log_file_name = f'Import_Log_{date.today()}_{uuid.uuid4()}.txt'
    log_path = os.path.join(log_dir, log_file_name)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(log_path, "w") as log_file:
        log_file.write("Sample Volume Import Log\n")
        log_file.write(f"Date: {date.today()}\n\n")

        # Loop through dataset and save the sample volumes to the database
        for index, row in cleaned_data.iterrows():
            try:
                session_id = int(row['id'])  # Ensure session_id is an integer
            except (ValueError, TypeError):
                sample_volumes_rejected['total_rejected'] += 1
                sample_volumes_rejected['session_ids'].append("N/A")
                sample_volumes_rejected['reason_for_rejection'].append(
                    "Invalid Session ID")
                log_rejection(log_file, "N/A", "Invalid Session ID")
                continue

            # Check if sample already exists
            if Sample_Volumes.objects.filter(session_id=session_id).exists():
                print(f"Sample with session_id {session_id} already exists.")
                continue  # Skip if it already exists

            # Create new sample volume
            new_sample_volume = Sample_Volumes()

            # Validate Sample Volume
            if not isinstance(row['collected'], bool) and isinstance(row['collected'], (int, float)) and not pd.isna(row['collected']):
                new_sample_volume.volume = int(row['collected'])
            else:
                sample_volumes_rejected['total_rejected'] += 1
                sample_volumes_rejected['session_ids'].append(session_id)
                sample_volumes_rejected['reason_for_rejection'].append(
                    "Reported volume missing")
                log_rejection(log_file, session_id, "Reported volume missing")
                continue

            # Validate Facility
            try:
                facility_code = int(row['facility'])
                new_sample_volume.facility = Facility.objects.get(
                    facility_code=facility_code)
            except (ValueError, Facility.DoesNotExist):
                sample_volumes_rejected['total_rejected'] += 1
                sample_volumes_rejected['session_ids'].append(session_id)
                sample_volumes_rejected['reason_for_rejection'].append(
                    "Facility not in database")
                log_rejection(log_file, session_id, "Facility not in database")
                continue

            # Assign remaining fields
            new_sample_volume.reported_date = row['date']
            new_sample_volume.reported_by = "+" + str(int(row['msisdn']))
            new_sample_volume.session_id = session_id

            # Save to database
            try:
                new_sample_volume.save()
                sample_volumes_added['total_added'] += 1
                sample_volumes_added['session_ids'].append(session_id)
                print(f"Sample {session_id} saved successfully.")
            except Exception as e:
                sample_volumes_rejected['total_rejected'] += 1
                sample_volumes_rejected['session_ids'].append(session_id)
                sample_volumes_rejected['reason_for_rejection'].append(
                    f"Database Error: {str(e)}")
                log_rejection(log_file, session_id,
                              f"Database Error: {str(e)}")
                continue

        # Write summary to log file
        log_file.write(
            f"\nTotal Samples Added: {sample_volumes_added['total_added']}\n")
        log_file.write(
            f"Total Samples Rejected: {sample_volumes_rejected['total_rejected']}\n")

        if sample_volumes_rejected['total_rejected'] > 0:
            log_file.write("\nRejected Samples:\nSession ID, Reason\n")
            for sid, reason in zip(sample_volumes_rejected['session_ids'], sample_volumes_rejected['reason_for_rejection']):
                log_file.write(f"{sid}, {reason}\n")

    # Return summary
    return f"Processing complete: {sample_volumes_added['total_added']} samples added, {sample_volumes_rejected['total_rejected']} rejected."
