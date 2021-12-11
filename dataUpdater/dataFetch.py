import pandas as pd
import os
import uuid
from datetime import datetime, date
from django.conf import settings

from sample_volumes.models import Sample_Volumes, Facility, SampleType

VALID_SAMPLE_CODES = [1, 2, 3, 4]


def _get_dataset():

    try:
        df = pd.read_csv(
            'C:/Users/LENOVO/Desktop/Excel files/sample_collection-20211208130041.csv')
        print('success fetching')
    except:
        return 'Error fetching'

    if df is not None:
        df['date'] = pd.to_datetime(df.date)
        start_day = '2021-12-07'
        end_day = '2021-12-09'

        # Convert start / end dates to datetime
        start_day = pd.to_datetime(start_day)
        end_day = pd.to_datetime(end_day)

        return df[df['date'].between(start_day, end_day)]


def updateData():
    sample_volume_data = _get_dataset()

    sample_volumes_added = {'total_added': 0, 'session_ids': []}

    sample_volumes_rejected = {'total_rejected': 0,
                               'session_ids': [], 'reason_for_rejection': []}

    if sample_volume_data is not None:
        # Open file to log the
        log_dir = f'{settings.BASE_DIR}\logs'
        log_file_name = f'Import Log {date.today()}_{uuid.uuid4()}.txt'
        filepath = os.path.join(log_dir, log_file_name)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        f = open(filepath, "w")

        # Loop through dataset and save the sample volumes to the database
        for index, row in sample_volume_data.iterrows():
            new_sample_volume = Sample_Volumes()

            if int(row['sample'] in VALID_SAMPLE_CODES):
                new_sample_volume.sample_type = SampleType.objects.get(
                    sample_code=int(row['sample']))
            else:
                sample_volumes_rejected['total_rejected'] += 1
                sample_volumes_rejected['session_ids'].append(row['session'])
                sample_volumes_rejected['reason_for_rejection'].append(
                    'Invalid Sample Code')
                continue
            if not isinstance(row['collected'], bool) and isinstance(row['collected'], (int, float)) and not pd.isna(row['collected']):
                new_sample_volume.volume = int(row['collected'])
            else:
                sample_volumes_rejected['total_rejected'] += 1
                sample_volumes_rejected['session_ids'].append(row['session'])
                sample_volumes_rejected['reason_for_rejection'].append(
                    'Reported volume missing')
                continue

            try:
                new_sample_volume.facility = Facility.objects.get(
                    facility_code=row['facility'])
            except:
                sample_volumes_rejected['total_rejected'] += 1
                sample_volumes_rejected['session_ids'].append(row['session'])
                sample_volumes_rejected['reason_for_rejection'].append(
                    'facility not in database')
                continue

            new_sample_volume.reported_date = row['date']
            new_sample_volume.reported_by = row['msisdn']

            new_sample_volume.save()
            sample_volumes_added['total_added'] += 1
            sample_volumes_added['session_ids'].append(row['session'])
            print("saving..")

        # Log the records that have been added
        f.write(
            f'Total Records Added {sample_volumes_added["total_added"]} \n')
        f.write("#.,ID\n")
        i = 0

        for added in sample_volumes_added['session_ids']:
            f.write(f'{i},{added}\n')
            i += 1

        # Log the records that have been rejected
        f.write(
            f'Total Records Reject {sample_volumes_rejected["total_rejected"]} \n')
        # f.write("#,ID,Reason for rejection\n")
        # i = j = 0
        # for (rejected, reason) in zip(sample_volumes_rejected['total_rejected'], sample_volumes_rejected['reason_for_rejection']):
        #     f.write(f'{i},{rejected},{reason}\n')

        f.close()

    else:
        return 'no data set'
