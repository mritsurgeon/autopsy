# Veeam Autopsy Integration Script

This script integrates Veeam Backup & Replication with Autopsy, a digital forensics platform, to facilitate forensic investigation of backed up data. It automates the process of restoring the latest restore point from Veeam backup and mounts it for analysis in Autopsy.

This will help with Law Enforcement and Forensics using BackupHhistorical images to collect evidence and report on Incident / Attack

## Setup
Before using the script, make sure to set the following variables:

```python
veeam_server = "10.0.0.1" # Veeam Backup & Replication server IP/FQDN address
mount_server = "10.0.0.1" # Server IP/FQDN address where the backup will be mounted
username = f"administrator@{mount_server}" # Username for accessing mount server , we using $ share
password = "Veeam123" # Password for accessing mount server over network $ share
api_user = "administrator" # Veeam API user to get OAuth Token
api_password = "Veeam123" # Veeam API password to get OAuth Token
case_number_ID = "x12jz" # Identifier for the case in Autopsy ( law enforecemnt or internal Incident ID)
autopsy_path = r"C:\Program Files\Autopsy-4.20.0\bin" # Path to Autopsy installation directory
triage_folder = r'C:\triage' # Folder where the restored data will be mounted for analysis on local Server & CASE files
```

## how it works 
1. The script first obtains an access token from the Veeam API using the provided credentials.
2. It then fetches the latest restore point data from Veeam backup. Please check ths section for more configurables Options
3. The latest restore point, filtered based on allowed operations, is selected for restoration.
4. The script initiates the restoration process.
5. After the restoration is completed, it waits for 2 minutes (120 seconds) to ensure the restored data is available. This can be changed if more or less time is needed.
6. It mounts the restored data on the network path and creates symbolic links in the triage folder.
7. Finally, it constructs and executes a command to launch Autopsy with the restored data for forensic analysis.

## Usauge 
1. Set the required variables at the beginning of the script.
2. Run the script using Python.
3. Autopsy will be launched automatically after the restoration process is completed.

## Note 
- Ensure that Veeam Backup & Replication is properly configured and accessible before running the script.
- Autopsy must be installed on the system and the path to its executable must be correctly specified.
