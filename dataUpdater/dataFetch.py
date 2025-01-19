import pandas as pd
import os
import uuid
from datetime import datetime, date, timedelta
from django.conf import settings
from .data_pull import pull
import pytz

from sample_volumes.models import Sample_Volumes, Facility, SampleType, DataUpdate

VALID_SAMPLE_CODES = [1, 2, 3, 4, 6]


def _get_dataset(latest_file):

    # Read in the file
    with open('/home/routeopt-user/st_optimization/reported_volumes/'+latest_file, 'r') as file:
        # with open('C:/Users/itszw/Dev/st_optimization/reported_volumes/'+latest_file, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('* Closing connection 0\n', '')
    filedata = filedata.replace('* Closing connection 0', '')

    # Write the file out again
    with open('/home/routeopt-user/st_optimization/reported_volumes/'+latest_file, 'w') as file:
        # with open('C:/Users/itszw/Dev/st_optimization/reported_volumes/'+latest_file, 'w') as file:
        file.write(filedata)

    try:
        df = pd.read_csv(
            '/home/routeopt-user/st_optimization/reported_volumes/'+latest_file)
        # df = pd.read_csv(
        #     'C:/Users/itszw/Dev/st_optimization/reported_volumes/'+latest_file)
        print('success fetching')
    except:
        return 'Error fetching'

    date_today = datetime.now() + timedelta(days=1)
    date_yesterday = date_today - timedelta(days=8)

    if df is not None:
        df['date'] = pd.to_datetime(df.date)
        start_day = date_today.strftime("%Y-%m-%d")
        end_day = date_yesterday.strftime("%Y-%m-%d")

        # Convert start / end dates to datetime
        start_day = pd.to_datetime(start_day)
        end_day = pd.to_datetime(end_day)

        return df[df['date'].between(end_day, start_day)]

# This is the function that starts a calls the data pull and processes the pulled data
# and saves each reported sample re


def updateData(downloaded=False):

    current_update = DataUpdate.objects.filter(
        completed=False).order_by('-created_at').first()

    update = DataUpdate()

    if not downloaded:
        if current_update:
            current_update.completed = True
            current_update.time_completed = datetime.now()
            current_update.save()
        else:
            update.completed = False
            update.user = 'system'
            update.save()
    else:
        update = current_update

    try:
        latest_file = pull()

        sample_volume_data = None

        if latest_file:
            sample_volume_data = _get_dataset(latest_file)

        sample_volumes_added = {'total_added': 0, 'session_ids': []}

        sample_volumes_rejected = {'total_rejected': 0,
                                   'session_ids': [], 'reason_for_rejection': []}

        if sample_volume_data is not None:
            # Open file to log the
            log_dir = f'{settings.BASE_DIR}{os.sep}logs'
            log_file_name = f'Import Log {date.today()}_{uuid.uuid4()}.txt'
            filepath = os.path.join(log_dir, log_file_name)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            f = open(filepath, "w")

            # Loop through dataset and save the sample volumes to the database
            for index, row in sample_volume_data.iterrows():
                if int(row['id']) == 424367:
                    print("my plasma")
                try:
                    reported_volume_object = Sample_Volumes.objects.get(
                        session_id=int(row['id']))
                except:
                    reported_volume_object = None

                if not reported_volume_object:
                    new_sample_volume = Sample_Volumes()

                    if int(row['sample'] in VALID_SAMPLE_CODES):
                        new_sample_volume.sample_type = SampleType.objects.get(
                            sample_code=int(row['sample']))
                    else:
                        sample_volumes_rejected['total_rejected'] += 1
                        sample_volumes_rejected['session_ids'].append(
                            row['session'])
                        sample_volumes_rejected['reason_for_rejection'].append(
                            'Invalid Sample Code')
                        continue
                    if not isinstance(row['collected'], bool) and isinstance(row['collected'], (int, float)) and not pd.isna(row['collected']):
                        new_sample_volume.volume = int(row['collected'])
                    else:
                        sample_volumes_rejected['total_rejected'] += 1
                        sample_volumes_rejected['session_ids'].append(
                            row['session'])
                        sample_volumes_rejected['reason_for_rejection'].append(
                            'Reported volume missing')
                        continue

                    try:
                        new_sample_volume.facility = Facility.objects.get(
                            facility_code=int(row['facility']))
                    except:
                        sample_volumes_rejected['total_rejected'] += 1
                        sample_volumes_rejected['session_ids'].append(
                            row['session'])
                        sample_volumes_rejected['reason_for_rejection'].append(
                            'facility not in database')
                        continue

                    new_sample_volume.reported_date = row['date']
                    new_sample_volume.reported_by = "+" + \
                        str(int(row['msisdn']))
                    new_sample_volume.session_id = int(row['id'])

                    new_sample_volume.save()
                    sample_volumes_added['total_added'] += 1
                    sample_volumes_added['session_ids'].append(row['session'])
                    print("saving..")
                else:
                    print("Sample already exists")

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
            update.time_completed = datetime.now()
            update.completed = True
            update.save()
            return

        else:
            update.time_completed = datetime.now()
            update.completed = True
            update.save()
            return 'no data set'
    except:
        if update:
            update.delete()
        return
