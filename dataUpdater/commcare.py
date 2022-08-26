import os
import requests
import json
import uuid
from datetime import date, datetime, timedelta
from django.conf import settings
from sample_volumes.models import (
    District,
    Route,
    Facility,
    Courier,
    Health_Worker,
    Sample_Volumes,
    Visit,
    Trip,
    SAMPLE_TYPE,
    STATUS,
)
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

os.putenv('CCHQ_API_AUTH',
          'ApiKey zgolowa@r4hmw.org:6ea3c44d076af61142b613e236809f2789c8eac9')


def fetch(start_date, end_date, case_type):
    payload = {}
    headers = {"Authorization": os.environ["CCHQ_API_AUTH"]}
    # device modified data
    # url = f'https://www.commcarehq.org/a/sample-22/api/v0.4/case/?format=json&type={case_type}&limit=5000&date_modified_start={start_date}&date_modified_end={end_date}&order_by=date_modified'
    url = f"https://www.commcarehq.org/a/sample-22/api/v0.4/case/?format=json&type={case_type}&limit=5000&server_date_modified_start={start_date}&server_date_modified_end={end_date}&order_by=server_date_modified"
    response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(response.text)
    return response


def get_visits():
    # Open file to log the
    log_dir = f"{settings.BASE_DIR}{os.sep}logs"
    log_file_name = f"get_visits_log_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{uuid.uuid4()}.txt"
    filepath = os.path.join(log_dir, log_file_name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    f = open(filepath, "w")

    error_data = []
    success_data = []

    # start_date = date(year=2021, month=11, day=30)
    start_date = date.today() - timedelta(days=10)
    start_date = start_date.strftime("%Y-%m-%d")

    end_date = date.today() + timedelta(days=1)
    end_date = end_date.strftime("%Y-%m-%d")

    case_type = "facility_visit"
    district = ""
    facility = ""
    courier = ""
    samples = {}
    results = {}

    data = fetch(start_date, end_date, case_type)

    visit_data = data["objects"]
    visit_data.reverse()

    for visit in visit_data:
        try:
            exists = Visit.objects.get(visit_id=visit["case_id"])
            if exists:
                continue
        except ObjectDoesNotExist:
            pass

        # Get the facility
        try:
            facility = Facility.objects.get(
                commcare_name=visit["properties"]["facility_name"]
            )
            district = facility.district
        except ObjectDoesNotExist:
            error = {"case_id": visit["case_id"],
                     "error": "Facility doesn't exist"}
            error_data.append(error)
            print("Facilitiy doesn't exist")
            continue
        except MultipleObjectsReturned:
            error = {
                "case_id": visit["case_id"],
                "error": "Multiple facilities have that name",
            }
            error_data.append(error)
            print("Multiple facilities have that name")
            continue

        # Get the courier
        try:
            courier = Courier.objects.get(commcare_user_id=visit["opened_by"])
        except ObjectDoesNotExist:
            error = {"case_id": visit["case_id"],
                     "error": "Courier doesn't exist"}
            error_data.append(error)
            print("Courier doesn't exist")
            continue
        except MultipleObjectsReturned:
            error = {
                "case_id": visit["case_id"],
                "error": "Multiple couriers have that id",
            }
            error_data.append(error)
            print("Multiple couriers have that name")
            continue

        new_visit = Visit()
        new_visit.visit_id = visit["case_id"]
        new_visit.visit_date = datetime.strptime(
            visit["properties"]["date_of_visit"], "%Y-%m-%d"
        )
        new_visit.status = STATUS[0][0]

        new_visit.facility = facility
        new_visit.district = district
        new_visit.courier = courier

        for st in SAMPLE_TYPE:
            if st[1] + "_samples" in visit["properties"]:
                samples.update(
                    {st[1]: int('0'+visit["properties"][st[1] + "_samples"])})
            else:
                samples.update(
                    {st[1]: 0})
            if st[1] + "_results" in visit["properties"]:
                results.update(
                    {st[1]: int('0'+visit["properties"][st[1] + "_results"])})
            else:
                results.update(
                    {st[1]: 0})

        new_visit.sample_volumes = json.dumps(samples)
        new_visit.results = json.dumps(results)

        new_visit.save()
        success = {"case_id": visit["case_id"]}
        success_data.append(success)

    i = 1
    f.write(f"Total Visits Successfully Saved: {len(success_data)}")
    f.write("#, id, message")
    for data in success_data:
        f.write(f'{i},{data["case_id"]},success\n')
        i += 1

    i = 1
    f.write(f"Total Visits With Errors: {len(error_data)}")
    f.write("#, id, message")
    for data in error_data:
        f.write(f'{i},{data["case_id"]},{data["error"]}\n')
        i += 1

    f.close()


def get_trips():
    # Open file to log the
    log_dir = f"{settings.BASE_DIR}\logs"
    log_file_name = (
        f"get_trips_log_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{uuid.uuid4()}.txt"
    )
    filepath = os.path.join(log_dir, log_file_name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    f = open(filepath, "w")

    error_data = []
    success_data = []

    # start_date = date(year=2021, month=11, day=30)
    start_date = date.today() - timedelta(days=10)
    start_date = start_date.strftime("%Y-%m-%d")

    end_date = date.today() + timedelta(days=1)
    end_date = end_date.strftime("%Y-%m-%d")

    case_type = "trip"
    district = ""
    start_location = ""
    end_location = ""
    courier = ""

    data = fetch(start_date, end_date, case_type)

    trip_data = data["objects"]
    trip_data.reverse()

    for trip in trip_data:
        try:
            exists = Trip.objects.get(trip_id=trip["case_id"])
            if exists:
                continue
        except ObjectDoesNotExist:
            pass

        # Get the start location
        try:
            start_location = Facility.objects.get(
                commcare_name=trip["properties"]["start_location"]
            )
            district = start_location.district
        except KeyError:
            error = {
                "case_id": trip["case_id"],
                "error": "Start location key not present in data",
                "name":  trip["properties"]["district"],
            }
        except ObjectDoesNotExist:
            error = {
                "case_id": trip["case_id"],
                "error": "Start location doesn't exist",
                "name": trip["properties"]["start_location"]
                + "_"
                + trip["properties"]["district"],
            }
            error_data.append(error)
            print("Start location doesn't exist")
            continue
        except MultipleObjectsReturned:
            error = {
                "case_id": trip["case_id"],
                "error": "Multiple locations have that name",
                "name": trip["properties"][
                    "start_location" + "_" + trip["properties"]["district"]
                ],
            }
            error_data.append(error)
            print("Multiple start locations have that name")
            continue

        # Get the end location
        try:
            end_location = Facility.objects.get(
                commcare_name=trip["properties"]["end_location"]
            )
        except KeyError:
            error = {
                "case_id": trip["case_id"],
                "error": "End location key not present in data",
                "name":  trip["properties"]["district"],
            }
        except ObjectDoesNotExist:
            error = {
                "case_id": trip["case_id"],
                "error": "End location doesn't exist",
                "name": trip["properties"]["end_location"]
                + "_"
                + trip["properties"]["district"],
            }
            error_data.append(error)
            print("End location doesn't exist")
            continue
        except MultipleObjectsReturned:
            error = {
                "case_id": trip["case_id"],
                "error": "Multiple locations have that name",
                "name": trip["properties"]["end_location"]
                + "_"
                + trip["properties"]["district"],
            }
            error_data.append(error)
            print("Multiple end locations have that name")
            continue

        # Get the courier
        try:
            courier = Courier.objects.get(commcare_user_id=trip["opened_by"])
        except ObjectDoesNotExist:
            error = {
                "case_id": trip["case_id"],
                "error": "Courier doesn't exist",
                "name": trip["properties"]["rider"]
                + "_"
                + trip["properties"]["district"],
            }
            error_data.append(error)
            print("Courier doesn't exist")
            continue
        except MultipleObjectsReturned:
            error = {
                "case_id": trip["case_id"],
                "error": "Multiple couriers have that id",
                "name": trip["properties"]["rider"]
                + "_"
                + trip["properties"]["district"],
            }
            error_data.append(error)
            print("Multiple couriers have that name")
            continue

        new_trip = Trip()
        try:
            new_trip.trip_id = trip["case_id"]
            new_trip.trip_date = datetime.strptime(
                trip["properties"]["start_date"], "%Y-%m-%d"
            )
            new_trip.start_time = trip["properties"]["start_time"][:8]
            new_trip.end_time = trip["properties"]["end_time"][:8]
        except Exception as e:
            print("Unable to capture trip", e)
            continue

        new_trip.start_location = start_location
        new_trip.end_location = end_location
        new_trip.district = district
        new_trip.courier = courier

        new_trip.start_km = int(trip["properties"]["start_km_changed"])
        new_trip.end_km = int(trip["properties"]["end_km"])

        new_trip.status = STATUS[0][0]

        new_trip.save()
        success = {
            "case_id": trip["case_id"],
        }
        success_data.append(success)

    # write the success logs
    i = 1
    f.write(f"Total Visits Successfully Saved: {len(success_data)}")
    f.write("#, id, message")
    for data in success_data:
        f.write(f'{i},{data["case_id"]},success\n')
        i += 1

    # write the error logs
    i = 1
    f.write(f"Total Visits With Errors: {len(error_data)}")
    f.write("#, id, message")
    for data in error_data:
        f.write(f'{i},{data["case_id"]},{data["error"]},{data["name"]}\n')
        i += 1

    f.close()
