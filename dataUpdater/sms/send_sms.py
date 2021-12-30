from datetime import date, datetime, timedelta
import hashlib
import random
import requests
import phonenumbers
import json
from ...sample_volumes.models import Route, Facility, Health_Worker

# App variables
app_key = "600184"
app_password = "mit@uc&*!"


def send_sms(phone_number, message):
    timestamp = datetime.now()
    timestamp = timestamp.strftime("%Y%m%d%H%M%S")
    auth_key_string = app_key+timestamp+app_password
    auth_key = hashlib.md5(auth_key_string.encode('utf-8')).hexdigest()
    ref = timestamp+"N" + \
        phone_number.replace("+265", "")+str(random.randint(1001, 9999))
    phone_number = valid_number(phone_number)

    if phone_number:
        template = open('sms_template.json', 'r+')
        data = template.read()
        data = data.replace("[arg:timestamp]", timestamp)
        data = data.replace("[arg:auth]", auth_key)
        data = data.replace("[arg:ref]", auth_key)
        data = data.replace("[arg:message]", message)
        data = data.replace("[arg:phone_number]", phone_number)

        url = "http://206.225.81.36/ucm_api/index.php"
        header = {"Content-Type": "application/json"}
        request = requests.post(url=url, data=data, headers=header)
        request_data = json.loads(request.text)
        if str(request_data['code']) == "000":
            print(request.text)
            return "success"
        else:
            return ""


def valid_number(phone_number):
    p = phonenumbers.parse(phone_number, "MW")
    if phonenumbers.is_valid_number(p):
        return phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
    else:
        return False


def sms_notifications():
