from importlib.metadata import version
import time
import os
import datetime
import requests
import clamd
import argparse
import json

REPOSITORY = "https://github.com/hilderonny/taskworker-scanforvirus"
VERSION = "1.0.0"
LIBRARY = "clamd-" + version("clamd")
LOCAL_FILE_PATH = "./temp"

print(f'Virus Scanner Version {VERSION}')

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--taskbridgeurl', type=str, action='store', required=True, help='Root URL of the API of the task bridge to use, e.g. https://taskbridge.ai/')
parser.add_argument('--clamdip', type=str, action='store', required=True, help='IP address of the ClamD server (127.0.0.1)')
parser.add_argument('--clamdport', type=str, action='store', required=True, help='Port of the ClamD server (3310)')
parser.add_argument('--version', '-v', action='version', version=VERSION)
parser.add_argument('--worker', type=str, action='store', required=True, help='Unique name of this worker')
args = parser.parse_args()

WORKER = args.worker
print(f'Worker name: {WORKER}')
TASKBRIDGEURL = args.taskbridgeurl
if not TASKBRIDGEURL.endswith("/"):
    TASKBRIDGEURL = f"{TASKBRIDGEURL}/"
APIURL = f"{TASKBRIDGEURL}api/"
print(f'Using API URL {APIURL}')

# Prepare temp path
os.makedirs(LOCAL_FILE_PATH, exist_ok=True)

# Open ClamD connection
CLAMDIP = args.clamdip
CLAMDPORT = int(args.clamdport)
print(f'Using ClamD Server {CLAMDIP}:{CLAMDPORT}')
cd = clamd.ClamdNetworkSocket()
cd.__init__(host=CLAMDIP, port=CLAMDPORT, timeout=None)

def process_file(file_path):
    result = {}
    try:
        print("Processing file " + file_path)
        clamd_response = cd.scan(file_path)
        print(clamd_response)
        clamd_result = next(iter(clamd_response.values()))
        print(clamd_result)

        result["status"] = clamd_result[0]
        if (clamd_result[0] == "FOUND"):
            result["detection"] = clamd_result[1]
        if (clamd_result[0] == "ERROR"):
            result["error"] = clamd_result[1]
    except Exception as ex:
        result["error"] = str(ex)
    return result

def check_and_process_files():

    start_time = datetime.datetime.now()
    take_request = {}
    take_request["type"] = "scanforvirus"
    take_request["worker"] = WORKER
    response = requests.post(f"{APIURL}tasks/take/", json=take_request)
    if response.status_code != 200:
        return False
    task = response.json()
    taskid = task["id"]
    print(json.dumps(task, indent=2))

    file_response = requests.get(f"{APIURL}tasks/file/{taskid}")
    local_file_path = os.path.abspath(os.path.join(LOCAL_FILE_PATH, taskid))
    with open(local_file_path, 'wb') as file:
        file.write(file_response.content)

    result_to_report = {}
    result_to_report["result"] = process_file(local_file_path)
    end_time = datetime.datetime.now()
    result_to_report["result"]["duration"] = (end_time - start_time).total_seconds()
    result_to_report["result"]["repository"] = REPOSITORY
    result_to_report["result"]["version"] = VERSION
    result_to_report["result"]["library"] = LIBRARY
    print(json.dumps(result_to_report, indent=2))
    print("Reporting result")
    requests.post(f"{APIURL}tasks/complete/{taskid}/", json=result_to_report)
    os.remove(local_file_path)
    print("Done")
    return True

try:
    print('Waiting for ClamD to come up')
    while True:
        try:
            cd.ping()
            break
        except Exception:
            pass
    print('Ready and waiting for action')
    while True:
        file_was_processed = False
        try:
            file_was_processed = check_and_process_files()
        except Exception as ex:
            print(ex)
        if file_was_processed == False:
            time.sleep(3)
except Exception:
    pass
