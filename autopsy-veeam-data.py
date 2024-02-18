import requests
import os
import subprocess 
import shutil
from tqdm import tqdm
import time

# Set these variables
veeam_server = "172.21.234.10"
mount_server = "172.21.234.10"
username = f"administrator@{mount_server}"
password = "Veeam123"
api_user = "administrator"
api_password = "Veeam123"
case_number_ID = "x12jz"
autopsy_path = r"C:\Program Files\Autopsy-4.20.0\bin"
# need a investigation folder 
triage_folder = r'C:\triage'



# First API call to obtain the access token
token_url = f"https://{veeam_server}:9419/api/oauth2/token"

payload = {
    "grant_type": "password",
    "username": api_user,
    "password": api_password,
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "x-api-version": "1.1-rev1"
}

try:
    response = requests.post(token_url, data=payload, headers=headers, verify=False)
    response.raise_for_status() 
    Userdata = response.json()
    access_token = Userdata.get("access_token")
    print(access_token)
except requests.exceptions.RequestException as e:
    print("Error:", e)

# Second API call to fetch restore points data
restore_points_url = f"https://{veeam_server}:9419/api/v1/objectRestorePoints"

query = {
    "skip": "0",
    "limit": "0",
    "orderColumn": "CreationTime",
    "orderAsc": "true",
    "malwareStatusFilter": "infected",
}

headers = {
    "x-api-version": "1.1-rev1",
    "Authorization": f"Bearer {access_token}" 
}

try:
    response = requests.get(restore_points_url, headers=headers, params=query, verify=False)
    response.raise_for_status() 
    RestorePointsData = response.json()
except requests.exceptions.RequestException as e:
    print("Error:", e)

# Extracting data from the response
data = RestorePointsData["data"]

# Filtering out items with allowed operation equals "StartFlrRestore"
filtered_data = [item for item in data if "StartFlrRestore" in item.get("allowedOperations", [])]

# filtered data
latest_RestorePoint = (filtered_data[0])
latest_id = latest_RestorePoint.get("id")
# Third API call to perform restore
restore_url = f"https://{veeam_server}:9419/api/v1/restore/flr"

payload = {
  "restorePointId": latest_id,
  "type": "Windows",
  "autoUnmount": {
    "enabled": True,
    "noActivityPeriodInMinutes": 180
  },
  "reason": "Autopsy"
  
}
headers = {
    "Content-Type": "application/json",
    "x-api-version": "1.1-rev1",
    "Authorization": f"Bearer {access_token}"
}

try:
    response = requests.post(restore_url, json=payload, headers=headers, verify=False)
    response.raise_for_status() 
    mounts = response.json()
    print(mounts)
except requests.exceptions.RequestException as e:
    print("Error:", e)

# Loading section with progress bar
print("Loading...FLR")
for _ in tqdm(range(120), desc="Progress", unit="s"):
    time.sleep(1)

# Network path
network_path = rf'\\{mount_server}\C$\VeeamFLR'

# Fetch directories
directories = [d for d in os.listdir(network_path) if os.path.isdir(os.path.join(network_path, d))]

# Print the directories
print("Directories:")
for directory in directories:
    print(directory)

# Filter network paths to only include those with "Volume1" subfolder
network_paths = [fr'\\{mount_server}\C$\VeeamFLR\{directory}' for directory in directories if os.path.exists(os.path.join(fr'\\{mount_server}\C$\VeeamFLR\{directory}', "Volume1"))]

# Print filtered network paths
print("Filtered Network Paths:")
for path in network_paths:
    print(path)

# Create the triage folder if it doesn't exist
if not os.path.exists(triage_folder):
    os.makedirs(triage_folder)

# Create symbolic links
for network_path in network_paths:
    directory_name = os.path.basename(network_path)
    link_name = os.path.join(triage_folder, directory_name)
    
    # Create symbolic link only if it doesn't already exist
    if not os.path.exists(link_name):
        os.symlink(network_path, link_name)


# Print symbolic links
print("Symbolic Links:")
for link in os.listdir(triage_folder):
    link_path = os.path.join(triage_folder, link)
    if os.path.islink(link_path):
        target_path = os.readlink(link_path)
        print(f"{link} -> {target_path}")

# Constructing the command to execute Autopsy
command = rf'"{autopsy_path}\autopsy64.exe" --createCase --addDataSource --caseName="{case_number_ID}" --caseType=single --caseBaseDir="{triage_folder}" --dataSourcePath="{triage_folder}"'
# optional --runIngest command = rf'"{autopsy_path}\autopsy64.exe" --createCase --addDataSource --caseName="{case_number_ID}" --caseType=single --caseBaseDir="{triage_folder}" --dataSourcePath="{triage_folder}"'
# This will take much longer as it will run ingets modules against data before opening Autopys 
# Printing the command
print("Command to execute Autopsy:", command)

# Execute the command using subprocess.run()
subprocess.run(command, shell=True)
print("launching Autopsy")
commandfinal = rf'"{autopsy_path}\autopsy64.exe"'
subprocess.run(commandfinal, shell=True)
