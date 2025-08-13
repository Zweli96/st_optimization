from datetime import date, datetime, timedelta
import hashlib
import random
import requests
import phonenumbers
import json
from sample_volumes.models import Route, Facility, Health_Worker, Sample_Volumes, SAMPLE_TYPE
from django.conf import settings
import os
import uuid

from sample_volumes.views import facilities

# App variables
app_key = "600184"
app_password = "mit@uc&*!"

sms_template_dir = f'{settings.BASE_DIR}{os.sep}json'
sms_template_name = 'sms_template.json'
sms_template_path = os.path.join(sms_template_dir, sms_template_name)


def send_sms(phone_number, message):
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        auth_key_string = app_key + timestamp + app_password
        auth_key = hashlib.md5(auth_key_string.encode('utf-8')).hexdigest()
        ref = f"{timestamp}N{phone_number.replace('+265', '')}{random.randint(1001, 9999)}"
        phone_number = valid_number(phone_number)

        if phone_number:
            with open(sms_template_path, 'r') as template:
                data = template.read()
            data = data.replace("[arg:timestamp]", timestamp)
            data = data.replace("[arg:auth]", auth_key)
            data = data.replace("[arg:ref]", auth_key)
            data = data.replace("[arg:message]", message)
            data = data.replace("[arg:phone_number]", phone_number)

            url = "http://206.225.81.36/ucm_api/index.php"
            header = {"Content-Type": "application/json"}
            try:
                request = requests.post(
                    url=url, data=data, headers=header, timeout=10)
                request.raise_for_status()
                request_data = json.loads(request.text)

                if str(request_data.get('code')) == "000":
                    print(f"[SUCCESS] SMS sent to {phone_number} | Ref: {ref}")
                    status = "success"
                    code = request_data['code']
                else:
                    status = "failure"
                    code = request_data.get('code', 'no code')
                    print(
                        f"[FAILURE] SMS to {phone_number} failed with code: {code}")

            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Failed to send SMS to {phone_number}: {e}")
                status = "error"
                code = "network_error"

            return {"status": status, "code": code, "ref": ref}

        else:
            print(f"[INVALID] Phone number invalid: {phone_number}")
            return {"status": "invalid_number", "code": None, "ref": None}

    except Exception as e:
        print(
            f"[EXCEPTION] Unexpected error in send_sms for {phone_number}: {e}")
        return {"status": "exception", "code": None, "ref": None}


def valid_number(phone_number):
    p = phonenumbers.parse(phone_number, "MW")
    if phonenumbers.is_valid_number(p):
        return phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
    else:
        return False


def send_sms_notifications():

    to_visit_message = f'A courier will visit your facility on {date.today()}. Please prepare samples for transportation. Please send reports for all VL; EID; TB and Other samples by 2pm.'
    not_visiting_message = f'R4H couriers will not visit your facility on {date.today()}. You will be notified before the next visit. Please report all VL; EID; TB and Other samples by 2pm.'

    facilites = Route.objects.filter(
        route_date=date.today()).values_list('facilities', flat=True)
    health_workers = Health_Worker.objects.filter(facility__in=facilites)
    health_workers_not_visiting = Health_Worker.objects.exclude(
        id__in=health_workers)

    for hw in health_workers:
        if not hw.phone_number:
            print(
                f"[SKIP] No phone number for health worker ID {hw.id}")
            continue

        try:
            # Try parsing and validating the number
            parsed_number = phonenumbers.parse(
                str(hw.phone_number), "MW")  # "MW" for Malawi
            if not phonenumbers.is_valid_number(parsed_number):
                print(
                    f"[INVALID] Phone number for {hw.id} is not valid: {hw.phone_number}")
                continue

            send_sms(str(hw.phone_number), to_visit_message)

        except phonenumbers.NumberParseException as e:
            print(
                f"[PARSE ERROR] Could not parse number for {hw.id}: {hw.phone_number} ({e})")

    for hwnv in health_workers_not_visiting:
        if not hwnv.phone_number:
            print(
                f"[SKIP] No phone number for health worker ID {hwnv.id}")
            continue

        try:
            # Try parsing and validating the number
            parsed_number = phonenumbers.parse(
                str(hwnv.phone_number), "MW")  # "MW" for Malawi
            if not phonenumbers.is_valid_number(parsed_number):
                print(
                    f"[INVALID] Phone number for {hwnv.id} is not valid: {hwnv.phone_number}")
                continue

            send_sms(str(hwnv.phone_number), not_visiting_message)

        except phonenumbers.NumberParseException as e:
            print(
                f"[PARSE ERROR] Could not parse number for {hwnv.id}: {hwnv.phone_number} ({e})")


def send_sms_reminders():

    facilities = Facility.objects.all()

    facilities_not_yet_reported = []
    for facility in facilities:
        missing_volumes = []
        facility_volumes = Sample_Volumes.objects.filter(
            facility=facility, reported_date__date=date.today())
        if len(facility_volumes) > 0:
            for s in SAMPLE_TYPE:
                type_count = facility_volumes.filter(sample_type=s[0])
                if len(type_count) == 0:
                    missing_volumes.append(s[1])
        else:
            for s in SAMPLE_TYPE:
                missing_volumes.append(s[1])
        if len(missing_volumes) > 0:
            facilities_not_yet_reported.append(
                {"facility": facility, 'missing_volumes': missing_volumes})

    if len(facilities_not_yet_reported) > 0:
        for fnyr in facilities_not_yet_reported:
            health_workers = Health_Worker.objects.filter(
                facility=fnyr["facility"])
            missing_samples_string = str(", ".join(fnyr['missing_volumes']))

            reminder_message = "Your facility did not report [arg:sample_types] sample volumes by 2pm today. Please report as soon as possible using the *126*XXXX*Y# codes."
            reminder_message = reminder_message.replace(
                "[arg:sample_types]", missing_samples_string)

            for hw in health_workers:
                if not hw.phone_number:
                    print(
                        f"[SKIP] No phone number for health worker ID {hw.id}")
                    continue

                try:
                    # Try parsing and validating the number
                    parsed_number = phonenumbers.parse(
                        str(hw.phone_number), "MW")  # "MW" for Malawi
                    if not phonenumbers.is_valid_number(parsed_number):
                        print(
                            f"[INVALID] Phone number for {hw.id} is not valid: {hw.phone_number}")
                        continue

                    send_sms(str(hw.phone_number), reminder_message)

                except phonenumbers.NumberParseException as e:
                    print(
                        f"[PARSE ERROR] Could not parse number for {hw.id}: {hw.phone_number} ({e})")
