import paramiko
from scp import SCPClient
import sys
import os
import glob
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta
from django.conf import settings
from dataUpdater import dataFetch


def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

# you can also use progress4, which adds a 4th parameter to track IP and port
# useful with multiple threads to track source


def progress4(filename, size, sent, peername):
    sys.stdout.write("(%s:%s) %s's progress: %.2f%%   \r" % (
        peername[0], peername[1], filename, float(sent)/float(size)*100))

def pull():
    # see get most recent file
    # if the file is older than 30 minutes
    # if pull again then run recursively
    file, updated = getMostRecentFile()
    if updated:
        return file
    else:
        pull_direct()
        dataFetch.updateData(downloaded=True)
        return
    return


def getMostRecentFile():
    reported_volumes_dir = f"{settings.BASE_DIR}{os.sep}reported_volumes"
    list_of_files = glob.glob(f'{reported_volumes_dir}{os.sep}*.csv')

    try:
        latest_file = max(list_of_files, key=os.path.getmtime)
        head, tail = os.path.split(latest_file)

        two_minutes_ago = datetime.now() - timedelta(minutes=2)
        file_time = datetime.fromtimestamp(
            os.path.getmtime(os.path.join(head, tail)))
        if file_time < two_minutes_ago:
            current_data = False
        else:
            current_data = True

        return tail, current_data
    except:
        nothing = None
        return nothing, False
    return


def pull_direct():

    url = "http://206.225.84.201/riders_test/sample_collection_export.php"
    
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

    data = "type=csv&records=all&rndVal=0.28999320348498614"

    print("Downloading reported volumes")
    resp = requests.post(url, headers=headers, data=data)
    print("Download completed")

    print(resp.status_code)

    # To save to an absolute path.
    # using datetime module

    now = datetime.now()  # current date and time
    date_time_stamp = now.strftime("%Y%m%d%H%M%S")

    with open(f"{settings.BASE_DIR}{os.sep}reported_volumes{os.sep}sample_collection-{date_time_stamp}.csv", 'wb') as f:
        f.write(resp.content)
    return
