#!/usr/bin/env python3
"""
An example script to send data to CommCare using the Submission API

Usage:

    setx CCHQ_PROJECT_SPACE 'sample-22'
    setx CCHQ_CASE_TYPE 'route'
    setx CCHQ_USERNAME 'zgolowa@r4hmw.org'
    setx CCHQ_PASSWORD 'Linda15..'
    setx CCHQ_USER_ID 'd18362736224a4493fee8c07b5060a68'
    setx CCHQ_OWNER_ID 'f6e47268ae667e482d226309683c577a'

    
    $ export CCHQ_PROJECT_SPACE=sample-22
    $ export CCHQ_CASE_TYPE=route
    $ export CCHQ_USERNAME=zgolowa@r4hmw.org
    $ export CCHQ_PASSWORD=Linda15..
    $ export CCHQ_USER_ID=d18362736224a4493fee8c07b5060a68
    $ export CCHQ_OWNER_ID=f6e47268ae667e482d226309683c577a

    $ ./submit_data.py sample_data.csv

"""

# (Optional) Configure the following settings with your values

# An XML namespace to identify your XForm submission
from jinja2 import Template
import requests
from xml.etree import ElementTree as ET
from typing import Any, Iterable, List, Optional, Tuple
from http.client import responses as http_responses
from datetime import datetime, timezone
from dataclasses import dataclass
import uuid
import sys
import os
import csv
from ..models import District, Route
from django.conf import settings

os.putenv('CCHQ_PROJECT_SPACE', 'sample-22')
os.putenv('CCHQ_CASE_TYPE', 'route')
os.putenv('CCHQ_USERNAME', 'zgolowa@r4hmw.org')
os.putenv('CCHQ_PASSWORD', 'Linda15..')
os.putenv('CCHQ_USER_ID', 'd18362736224a4493fee8c07b5060a68')
os.putenv('CCHQ_OWNER_ID', 'f6e47268ae667e482d226309683c577a')

FORM_XMLNS = 'http://test.com/submission-api-example-form/'

# A string to identify the origin of your data
DEVICE_ID = "optimization_push_routes_example"

# End of configurable settings


COMMCARE_URL = 'https://www.commcarehq.org/'

CASE_UPDATE = False


@dataclass
class CaseProperty:
    name: str
    value: Any


@dataclass
class Case:
    id: str  # A UUID. Generated if not given in the data.
    name: str  # Required
    type: str  # A name for the case type. e.g. "person" or "site"
    modified_on: str  # Generated if not given. e.g. "2020-06-08T18:41:33.207Z"
    owner_id: str  # ID of the user or location that cases must be assigned to
    district: str  # ID of the user or location that cases must be assigned to
    day: str  # ID of the user or location that cases must be assigned to
    route: str  # ID of the user or location that cases must be assigned to
    route_date: str  # ID of the user or location that cases must be assigned to
    approved: str  # ID of the user or location that cases must be assigned to
    # ID of the user or location that cases must be assigned to
    confirmed: Optional[str]
    # ID of the user or location that cases must be assigned to
    confirmed_time: Optional[str]
    # ID of the user or location that cases must be assigned to
    added_facilities: Optional[str]
    properties: List[CaseProperty]  # All other given data
    server_modified_on: Optional[str]


def main(data, updated):
    """
    Sends data to CommCare HQ using the Submission API.
    """
    if updated:
        global CASE_UPDATE
        CASE_UPDATE = True
    # data = get_data(filename)
    cases = as_cases(data)
    xform_str = render_xform(cases)
    success, message = submit_xform(xform_str)
    return success, message


def get_data(csv_filename) -> Iterable[dict]:
    """
    Reads data in CSV format from the given filename, and yields it as
    dictionaries.
    """
    with open(csv_filename) as csv_file:
        reader = csv.DictReader(csv_file)
        yield from reader


def as_cases(data: Iterable[dict]) -> Iterable[Case]:
    """
    Casts dictionaries as Case instances
    """
    reserved = ('id', 'name', 'case_type', 'modified_on', 'server_modified_on')
    for dict_ in data:
        properties = [CaseProperty(name=key, value=value)
                      for key, value in dict_.items()
                      if key not in reserved]

        facilities = Route.objects.get(
            id=dict_["id"]).facilities.values_list('name', flat=True)
        if facilities:
            facilities = str(" ,".join(facilities))
        else:
            facilities = str('On call')
        yield Case(
            id=dict_.get('commcare_id'),
            name=f'{dict_["route_date"].strftime("%A")}{dict_["route_number"]}',
            type=os.environ['CCHQ_CASE_TYPE'],
            modified_on=dict_.get('modified_on', now_utc()),
            owner_id=District.objects.get(
                id=dict_["district"]).commcare_district_group_id,
            district=District.objects.get(id=dict_["district"]).name,
            day=f'{dict_["route_date"].strftime("%A")}',
            route=facilities,
            route_date=dict_.get('route_date'),
            server_modified_on=dict_.get('server_modified_on', updated_case()),
            approved='yes',
            confirmed=dict_.get('confirmed'),
            confirmed_time=dict_.get('confirmed_time'),
            added_facilities=dict_.get('added_facilities'),
            properties=properties,
        )


def render_xform(cases: Iterable[Case]) -> str:
    context = {
        'form_xmlns': FORM_XMLNS,
        'device_id': DEVICE_ID,
        'now_utc': now_utc(),
        'cchq_username': os.environ['CCHQ_USERNAME'],
        'cchq_user_id': os.environ['CCHQ_USER_ID'],
        'submission_id': uuid.uuid4().hex,
        'cases': list(cases),
    }
    temp_dir = f"{settings.BASE_DIR}\sample_volumes\commcare_submsission_api"
    temp_file_name = "xform.xml.j2"
    filepath = os.path.join(temp_dir, temp_file_name)

    # with open('D:/dev/st_optimization/sample_volumes/commcare_submsission_api/xform.xml.j2') as template_file:
    with open(filepath) as template_file:
        template = Template(template_file.read())
    xform = template.render(**context)
    return xform


def submit_xform(xform: str) -> Tuple[bool, str]:
    """
    Submits the given XForm to CommCare.

    Returns (True, success_message) on success, or (False,
    failure_message) on failure.
    """
    url = join_url(COMMCARE_URL,
                   f'/a/{os.environ["CCHQ_PROJECT_SPACE"]}/receiver/api/')
    auth = (os.environ['CCHQ_USERNAME'], os.environ['CCHQ_PASSWORD'])
    headers = {'Content-Type': 'text/html; charset=UTF-8'}
    response = requests.post(url, xform.encode('utf-8'),
                             headers=headers, auth=auth)
    if not 200 <= response.status_code < 300:
        return False, http_responses[response.status_code]
    return parse_response(response.text)


def parse_response(text: str) -> Tuple[bool, str]:
    """
    Parses a CommCare HQ Submission API response.

    Returns (True, success_message) on success, or (False,
    failure_message) on failure.

    >>> text = '''
    ... <OpenRosaResponse xmlns="http://openrosa.org/http/response">
    ...     <message nature="submit_success">   √   </message>
    ... </OpenRosaResponse>
    ... '''
    >>> parse_response(text)
    (True, '   √   ')

    """
    xml = ET.XML(text)
    message = xml.find('{http://openrosa.org/http/response}message')
    success = message.attrib['nature'] == 'submit_success'
    return success, message.text


def join_url(base_url: str, endpoint: str) -> str:
    """
    Returns ``base_url`` + ``endpoint`` with the right forward slashes.

    >>> join_url('https://example.com/', '/api/foo')
    'https://example.com/api/foo'
    >>> join_url('https://example.com', 'api/foo')
    'https://example.com/api/foo'

    """
    return '/'.join((base_url.rstrip('/'), endpoint.lstrip('/')))


def now_utc() -> str:
    """
    Returns a UTC timestamp in ISO-8601 format with the offset as "Z".
    e.g. "2020-06-08T18:41:33.207Z"
    """
    now = datetime.now(tz=timezone.utc)
    now_iso = now.isoformat(timespec='milliseconds')
    now_iso_z = now_iso.replace('+00:00', 'Z')
    return now_iso_z


def updated_case() -> str:
    """
    Returns a UTC timestamp if the case is being updated on CommCare
    """

    if CASE_UPDATE:
        return now_utc()
    else:
        return


def missing_env_vars():
    env_vars = (
        'CCHQ_PROJECT_SPACE',
        'CCHQ_CASE_TYPE',
        'CCHQ_USERNAME',
        'CCHQ_PASSWORD',
        'CCHQ_USER_ID',
        'CCHQ_OWNER_ID',
    )
    return [env_var for env_var in env_vars if env_var not in os.environ]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit()
    if missing := missing_env_vars():
        print('Missing environment variables:', ', '.join(missing))
        sys.exit(1)
    success, message = main(sys.argv[1])
    print(message)
    if not success:
        sys.exit(1)
