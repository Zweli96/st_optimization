import paramiko
from scp import SCPClient
import sys
import os
import glob


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
    ssh = createSSHClient('eosloan.mit.edu', 22, 'zgolowa', 'RxxZXX10..44')
    scp = SCPClient(ssh.get_transport(), progress4=progress4)

    # scp.get(remote_path="/home/zgolowa/projects/STOpt_proj/USSD_Data/push/ussd.proj/sample_collection-20211216214540.csv",
    #         local_path="C:/Users/itszw/Desktop/Sample Volumes/sample_collection-20211216214540.csv")

    sftp = ssh.open_sftp()
    sftp.chdir("/home/zgolowa/projects/STOpt_proj/USSD_Data/push/ussd.proj")

    latest = 0
    latestfile = None

    for fileattr in sftp.listdir_attr():
        if fileattr.filename.startswith('sample_collection') and fileattr.st_mtime > latest:
            latest = fileattr.st_mtime
            latestfile = fileattr.filename

    if latestfile is not None:
        if latestfile != getMostRecentFile():
            print('newer file available \n downloading latest file')
            scp.get("/home/zgolowa/projects/STOpt_proj/USSD_Data/push/ussd.proj/" +
                    latestfile, "C:/Users/itszw/Desktop/Sample Volumes/" + latestfile)
            return latestfile
        else:
            print("Data up to date")
            return False


def getMostRecentFile():
    # * means all if need specific format then *.csv
    list_of_files = glob.glob('C:/Users/itszw/Desktop/Sample Volumes/*.csv')
    latest_file = max(list_of_files, key=os.path.getmtime)
    head, tail = os.path.split(latest_file)
    return tail
