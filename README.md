# Uber Data Engineering Project

## Overview
End-to-end data pipeline processing ride-share data, demonstrating modern data engineering practices with cloud infrastructure, ETL orchestration, and analytics.

## Architecture
<img width="730" height="335" alt="architecture" src="https://github.com/user-attachments/assets/e1bd5fb0-9af7-48dc-a45b-81b3eb953513" />

## Tech Stack
- **Cloud Platform**: Google Cloud Platform (Compute Engine, Cloud Storage)
- **Orchestration**: Mage AI
- **Language**: Python
- **Data Warehouse**: BigQuery
- **Visualization**: Looker Studio

---

## Setup & Deployment

### 1. Create a GCP Account
Set up a Google Cloud account and create a new project.

### 2. Upload Data to Google Cloud Storage
Make the data file publicly accessible:
- Go to your GCS bucket → Permissions → Switch to **fine-grained**
- Set public access on the file

### 3. Deploy Mage on GCP Compute Engine
1. Create a VM Instance (E2, 4 cores, 16 GB RAM)
2. SSH into the VM from the GCP Console
3. Create and activate a virtual environment:
```bash
python3 -m venv ~/.venv
source ~/.venv/bin/activate
```
4. Install Mage:
```bash
pip install mage-ai
```
5. Create and start your project:
```bash
mage start uber_project
```
6. Add a **firewall rule** in GCP to allow traffic on port `6789` from your IP
7. Access Mage at `http://<your-vm-external-ip>:6789`
   - Default login: `admin@admin.com` / `admin`

> **Important:** Always start Mage from inside your project folder, not the home directory:
> ```bash
> cd ~/uber_project
> mage start uber_project
> ```

---

## Pipeline

### Step 1 — Load Data
Load ride-share data via API using the public GCS URL.

### Step 2 — Transform Data
Transform raw data into a star schema with dimension and fact tables:
- `dim_datetime`
- `dim_passenger_count`
- `dim_trip_distance`
- `dim_rate_code`
- `dim_pickup_location`
- `dim_dropoff_location`
- `dim_payment_type`
- `fact_table`

The transformer returns a **dictionary of DataFrames** so the exporter can load each table individually into BigQuery.

### Step 3 — Export to BigQuery
Configure `io_config.yaml` with GCP service account credentials:
- GCP Console → APIs & Services → Credentials → Create Service Account → Download JSON key
- Paste credentials into `io_config.yaml`

The exporter loops through the dictionary and loads each DataFrame into BigQuery one at a time:
```python
for table_name, df in data.items():
    # export df to BigQuery as table_name
```

### Step 4 — Analytics Layer
Join all dimension tables with the fact table in BigQuery to create a single analytics table for reporting.

### Step 5 — Looker Studio Dashboard
Connect BigQuery analytics table to Looker Studio and build the report.

---

## Version Control
```bash
# Make sure git is installed on your VM
sudo apt-get install git -y

# Initialize from inside your project folder
cd ~/uber_project
git add uber_project/data_loaders/dl_uber_data.py
git add uber_project/transformers/tf_uber_data.py
git add uber_project/pipelines/
git commit -m "uber project pipeline"
git push origin master
```
> **Never commit `io_config.yaml`** — it contains your GCP credentials. Add it to `.gitignore`.

---

## Encountered Errors & Solutions
Detailed troubleshooting notes are documented here: [ERRORS.md](ERRORS.md)
