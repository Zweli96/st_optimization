import os
import requests
import json
import uuid
from datetime import date, datetime, timedelta
from django.conf import settings
from sample_volumes.models import District, Route, Facility, Courier, Health_Worker, Sample_Volumes, Visit, Trip, SAMPLE_TYPE, STATUS
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


def fetch(start_date, end_date, case_type):
    payload = {}
    headers = {
        'Authorization': os.environ['CCHQ_API_AUTH']
    }
    # device modified data
    # url = f'https://www.commcarehq.org/a/sample-22/api/v0.4/case/?format=json&type={case_type}&limit=5000&date_modified_start={start_date}&date_modified_end={end_date}&order_by=date_modified'
    url = f'https://www.commcarehq.org/a/sample-22/api/v0.4/case/?format=json&type={case_type}&limit=5000&server_date_modified_start={start_date}&server_date_modified_end={end_date}&order_by=server_date_modified'
    response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(response.text)
    return response


def get_visits():
    # Open file to log the
    log_dir = f'{settings.BASE_DIR}\logs'
    log_file_name = f'get_visits_log_{date.today()}_{uuid.uuid4()}.txt'
    filepath = os.path.join(log_dir, log_file_name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    f = open(filepath, "w")

    error_data = []
    success_data = []

    # start_date = date(year=2021, month=11, day=30)
    start_date = date.today() - timedelta(days=1)
    start_date = start_date.strftime("%Y-%m-%d")

    end_date = date.today() + timedelta(days=1)
    end_date = end_date.strftime("%Y-%m-%d")

    case_type = 'facility_visit'
    district = ""
    facility = ""
    courier = ""
    samples = {}

    data = fetch(start_date, end_date, case_type)

    visit_data = data['objects']
    visit_data.reverse()

    for visit in visit_data:
        try:
            exists = Visit.objects.get(visit_id=visit['case_id'])
            if exists:
                break
        except ObjectDoesNotExist:
            pass

        # Get the facility
        try:
            facility = Facility.objects.get(
                commcare_name=visit['properties']['facility_name'])
            district = facility.district
        except ObjectDoesNotExist:
            error = {"case_id": visit['case_id'],
                     "error": "Facility doesn't exist"}
            error_data.append(error)
            print("Facilitiy doesn't exist")
            continue
        except MultipleObjectsReturned:
            error = {"case_id": visit['case_id'],
                     "error": "Multiple facilities have that name"}
            error_data.append(error)
            print("Multiple facilities have that name")
            continue

        # Get the courier
        try:
            courier = Courier.objects.get(
                commcare_user_id=visit['opened_by'])
        except ObjectDoesNotExist:
            error = {"case_id": visit['case_id'],
                     "error": "Courier doesn't exist"}
            error_data.append(error)
            print("Courier doesn't exist")
            continue
        except MultipleObjectsReturned:
            error = {"case_id": visit['case_id'],
                     "error": "Multiple couriers have that id"}
            error_data.append(error)
            print("Multiple couriers have that name")
            continue

        new_visit = Visit()
        new_visit.visit_id = visit['case_id']
        new_visit.visit_date = datetime.strptime(
            visit['properties']['date_of_visit'], "%Y-%m-%d")
        new_visit.status = STATUS[0][0]

        new_visit.facility = facility
        new_visit.district = district
        new_visit.courier = courier

        for st in SAMPLE_TYPE:
            samples.update({st[1]: int(visit['properties'][st[1]+'_samples'])})

        new_visit.sample_volumes = json.dumps(samples)

        new_visit.save()
        success = {"case_id": visit['case_id']}
        success_data.append(success)

    i = 1
    f.write(f'Total Visits Successfully Saved: {len(success_data)}')
    f.write('#, id, message')
    for data in success_data:
        f.write(f'{i},{data["case_id"]},success\n')
        i += 1

    i = 1
    f.write(f'Total Visits With Errors: {len(error_data)}')
    f.write('#, id, message')
    for data in error_data:
        f.write(f'{i},{data["case_id"]},{data["error"]}\n')
        i += 1

    f.close()
