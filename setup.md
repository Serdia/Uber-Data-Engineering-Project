# Uber-Data-Engineering-Project

# Real-Time Ride-Share Analytics Pipeline

## Overview
End-to-end data pipeline processing ride-share data, 
demonstrating modern data engineering practices with 
cloud infrastructure, ETL orchestration, and analytics.

## Tips
Activate .venv bein in home (~) directory (not project)
Start mage from project folder "Uber Projerct". Not from home directory(~)
Make sure to install github: ```sudo apt-get install git -y```

```(.venv) myusername@vm-uber-project:~/uber_project$ mage start uber_project```

## Create google cloud account

## Make data public so I can access it using my code:
<img width="959" height="173" alt="image" src="https://github.com/user-attachments/assets/09316d5c-6963-415f-858e-3f86a86cbb44" />

Permission Error. To fix it, go to "Permissions" --> "Switch to fine-grained"

<img width="623" height="247" alt="image" src="https://github.com/user-attachments/assets/b4418688-f237-4c8b-9213-faf60d4b610d" />

Now I am able to make it public:

<img width="603" height="353" alt="image" src="https://github.com/user-attachments/assets/703e82e3-fff2-4c35-bb22-4f7da0c842ac" />

## Deploy Mage to google compute engine
1. Create VM Instance E2 4 cores 16 Gb
   
<img width="1078" height="612" alt="image" src="https://github.com/user-attachments/assets/92ddbc6c-3a43-4524-811e-0d8038113fc9" />

2.Instance is ready

<img width="844" height="128" alt="image" src="https://github.com/user-attachments/assets/0cb3a82b-81e0-4a28-9239-27d2c6064d8d" />

3.Click on SSH to start interacting with VM via shell:

<img width="680" height="200" alt="image" src="https://github.com/user-attachments/assets/139ae79b-bea2-469d-a6b8-183e984c409e" />

4. In SSH terminal create virtual environment using command "python3 -m venv ~/.venv". 
5. Activate .venv: zoeyserdyuk@vm-uber-project:~$ ```source ~/.venv/bin/activate```
6. Install Mage using command: pip install mage-ai
7. Start Mage using command "Mage start myprojectname"
8. http://localhost:6789
9. Need to add firewall rule to accept request from 6789
   Use powershell to get your public IP address, run command (Invoke-WebRequest -Uri "https://api.ipify.org").Content
   Then enter it 94.205.121.45/32   32 means single IP address (for security)
10. If Mage server asking for login credentials, use : Email: admin@admin.com   Password: admin

## Create pipeline in Mage:

Load data using API, since my data is publicly available. 
<img width="626" height="370" alt="image" src="https://github.com/user-attachments/assets/ea8d9f03-265e-4d62-876d-54fe21476f3d" />

2. Copy URL from google storage and paste it in a code. Then click button to test the response to see the data.
   
<img width="797" height="695" alt="image" src="https://github.com/user-attachments/assets/a19ebcb0-f23d-4195-b029-558a8a4368ef" />

3. Add "Transformer" to transform our data
4. Chage return statement in transformer to make it dictionary of dataframes. So then exporter can accept it to BigQuery warehouse.
     return{
        "dim_datetime":dim_datetime,
        "dim_passanger_count":dim_passanger_count,
        "dim_trip_distance":dim_trip_distance,
        "dim_rate_code":dim_rate_code,
        "dim_pickup_location":dim_pickup_location,
        "dim_dropoff_location":dim_dropoff_location,
        "dim_payment_type":dim_payment_type,
        "fact":fact
    }

## pass this multiple dataframes to the loader function and load this data to the bigquery warehouse. We will pass those dataframe as a dictionary


## Configure Exporter:
1. In google cloud need to get credentials: APIs & Services --> Credentials --> Create credentials --> Service account
2. Create Account key and add it to io_config.yaml file
3. Since transformer returns dictionary of dataframes, we need to loop through each key value pair and export it to bigquery. Bq can only accept it one by one:
```python
    # loop through each table name in a dictionary
    # table_name = the name (key from dictionary) 
    # df = the DataFrame itself (value from dictionary)
    # data = the entire dictionary containing all table names and DataFrames
    for table_name, df in data.items():
```
<img width="536" height="361" alt="image" src="https://github.com/user-attachments/assets/9d6a5bd1-6b6c-4c0a-b6f7-dd0e2de76647" />

Pipeline fun succesfully:

<img width="279" height="418" alt="image" src="https://github.com/user-attachments/assets/ae6013be-5733-4ae6-b107-5f527f25f669" />

4. All tables succesfully created in BigQuery:
   
<img width="308" height="263" alt="image" src="https://github.com/user-attachments/assets/e3aa8666-0608-425c-a61f-cc48f66208d7" />

## Join fact table with all dimenstions table and create Analytic table to be used in Looker studio.

<img width="582" height="473" alt="image" src="https://github.com/user-attachments/assets/9d410fc8-b73b-4a20-a766-672dc6a6bcde" />

## Build report in looker studio




## Errors I encountered:
Error: Mage-AI Installation Issues on GCP VM
The Problem:
When trying to install mage-ai using the standard pip install mage-ai command, I encountered this error:
error: externally-managed-environment
× This environment is externally managed
Why This Happened:
Python 3.11+ introduced a security feature that prevents you from installing packages system-wide with pip. This is to protect the operating system's Python packages from being accidentally broken by user installations.
On Debian/Ubuntu systems (like GCP VMs), the system Python is "externally managed" meaning:

The OS uses Python for system tools
Installing random packages with pip could break system functionality
Python enforces separation between system packages and user packages

Why I Used pipx Instead of pip:
I initially tried pipx as an alternative to pip because:
pipx:

Designed for installing Python applications (like mage-ai, black, pytest)
Automatically creates isolated virtual environments for each application
Makes commands globally available without polluting system Python
Good for CLI tools you want to run from anywhere

The Real Solution:
pipx wasn't the right choice for mage-ai because:

Mage needs many dependencies (pandas, polars, pyarrow, etc.)
pipx creates isolated environments that make dependency management harder
The tutorial assumes a standard pip installation in a virtual environment.
So I decided to clean everything up and start over but using virtual environment 
Commands to remove installed items:
pipx uninstall mage-ai
rm -rf ~/myproject
sudo apt remove pipx

Error: ImportError: Pandas requires version '3.1.5' or newer of 'jinja2' (version '3.1.3' currently installed).
Basically Pandas needs a newer version of jinja2 than what's currently installed.
Run command: pip install --upgrade pandas jinja2

Error: Spark config got unexptected Error "Authentication".
Me playing around with removing login page, I hardcoded value "Authentication: mode: none" in metadata.yaml file. Removing it solved the problem.

<img width="873" height="676" alt="image" src="https://github.com/user-attachments/assets/985a5346-bdd3-454b-a23d-a4b8d5040f4c" />

Error: SyntaxError: unexpected character after line continuation character
Solution: avoided backslashes by wrapping Fact table creation in parentheses.

Error: Next day starting Mage I was not able to find files I created. Turned out I accidently created nested folder uber_project.
To fix that I moved files to proper location and then deleted empty folder uber_project.
(.venv) zoeyserdyuk@vm-uber-project:~/uber_project/uber_project/transformers$ mv transformer_uber_data.py ~/uber_project/transformers/

Error:
Constantly getting "Page Unresponsive" error clicking on Edit pipeline in Mage.
<img width="788" height="456" alt="image" src="https://github.com/user-attachments/assets/988871f7-5f4f-47fc-9dfa-f208a0610756" />
Seems like pipeline is corrupted. 
Deleting and re-creating a new pipeline hopefully resolve the problem.
cd ~
backup existing project: cp -r uber_project uber_project_backup
remove project: rm -rf uber_project
create new project: mage init uber_project
# Copy over just your code files (not metadata).
cd uber_project
cp ../uber_project_backup/transformers/*.py transformers/   # copy all .py files and put it into destination folder
cp ../uber_project_backup/data_loaders/*.py data_loaders/

Error: Mage UI did is not able to locate files in data loader and transformer. I tried to clear cache, refresh, restart mage etc. But nothing helped. Interestingly enough, I am able to view files using terminal. I guess its some kind of a bug. 
Solution: I re-created data loader and transformer.

Error: after entering connection information into io_config.yaml file getting this error:
<img width="658" height="172" alt="image" src="https://github.com/user-attachments/assets/43dea727-b0f8-4d8d-ae16-4968c16c52be" />
Solution: in key value pair I accidently hardcoded extra key:  client_x509_cert_url:. Removing that solved the problem.

Error: running data exporter got an error:

<img width="631" height="444" alt="image" src="https://github.com/user-attachments/assets/d5e59af0-4794-4773-adae-04c319956484" />
Need to install google cloud on VM instance.
Make sure venv is activated and type command: pip install google-cloud    and pip install google-cloud-bigquery


Error:
<img width="629" height="533" alt="image" src="https://github.com/user-attachments/assets/660f7ad4-8179-4fff-8e1c-c0a5a28513df" />
Dependency package need to be installed:  pip install db-dtypes.   Handles database data type conversions between BigQuery and pandas.

Error: 
Was not able to export to bigquery a dictionary of dataframes, because bigquery export() method only accepts one df at a time, not a dictionary.
Solution: need to loop through the dictionary of dataframes. 











