# Uber Data Engineering Project

## Overview

End-to-end data pipeline processing ride-share data, demonstrating modern data engineering practices with cloud infrastructure, incremental ETL orchestration, dbt transformations, and analytics.

## Architecture

<img width="730" height="335" alt="architecture" src="https://github.com/user-attachments/assets/e1bd5fb0-9af7-48dc-a45b-81b3eb953513" />

## Tech Stack

| Layer | Tool |
|---|---|
| Cloud Platform | Google Cloud Platform (Compute Engine, Cloud Storage) |
| Orchestration | Mage AI |
| Transformation | dbt (data build tool) |
| Language | Python |
| Data Warehouse | BigQuery |
| Visualization | Looker Studio |
| IDE | VS Code via Remote SSH |

---

## Pipeline

The pipeline runs 3 blocks in sequence inside Mage:

```
dl_get_data  →  exp_load_raw_data  →  exp_subprocess_run
(Data Loader)   (Data Exporter)        (Data Exporter)
```

### Block 1 — `dl_get_data` (Data Loader)

Loads only **new records** from the CSV using a watermark pattern:

1. Queries the BigQuery `fact` table for `MAX(tpep_pickup_datetime)` — the watermark
2. Loads the CSV from Google Cloud Storage
3. Filters rows where `tpep_pickup_datetime > watermark`
4. Returns only new records as a DataFrame (or an empty DataFrame if nothing is new)

> On the first run (when the `fact` table doesn't exist yet), the watermark defaults to `1900-01-01` so all records are loaded.

### Block 2 — `exp_load_raw_data` (Data Exporter)

Exports the raw, **untransformed** DataFrame directly into BigQuery as a staging table:

- Destination: `ds_uber_project.stg_uber_raw_data`
- Mode: `append` — new records are added incrementally, nothing is overwritten
- No transformations happen here — raw data lands exactly as-is

### Block 3 — `exp_subprocess_run` (Data Exporter)

Triggers **dbt** via Python's `subprocess` module to run all dbt models against the staging table:

- dbt reads from `stg_uber_raw_data` and builds the dimension and fact tables in BigQuery:
  - `dim_datetime`
  - `dim_passenger_count`
  - `dim_trip_distance`
  - `dim_rate_code`
  - `dim_pickup_location`
  - `dim_dropoff_location`
  - `dim_payment_type`
  - `fact`
- If dbt exits with a non-zero return code, the block raises an exception and the pipeline fails visibly

> **Why subprocess?** dbt cannot run natively inside Mage due to environment conflicts. It is installed in its own virtual environment (`dbt_env`) and called from Mage using `subprocess.run()`.

---

## Data Flow Summary

```
GCS CSV
  │
  ▼
[Block 1] Watermark filter → new records only
  │
  ▼
[Block 2] Append raw records → BigQuery: stg_uber_raw_data
  │
  ▼
[Block 3] subprocess → dbt run → BigQuery: dim_* + fact tables
  │
  ▼
Looker Studio Dashboard
```

---

## Project Structure

```
~/dbt_uber_project/
├── dbt_project.yml          # dbt project config (profile name must match profiles.yml)
├── packages.yml             # dbt package dependencies (dbt_utils)
├── profiles.yml             # BigQuery connection config (kept in project folder)
├── keys/
│   └── service-account.json # GCP service account key (never commit this)
├── models/
│   └── staging/
│       └── sources.yml      # tells dbt where raw data lives in BigQuery
└── dbt_packages/
    └── dbt_utils/           # auto-generated after dbt deps
```

---

## Version Control

```bash
sudo apt-get install git -y

cd ~/uber_project
git add uber_project/data_loaders/dl_get_data.py
git add uber_project/exporters/exp_load_raw_data.py
git add uber_project/exporters/exp_subprocess_run.py
git add uber_project/pipelines/
git commit -m "uber project pipeline"
git push origin master
```

> **Never commit** `io_config.yaml` or `keys/service-account.json` — both contain GCP credentials.

### Recommended `.gitignore`

```
io_config.yaml
keys/
*.json
dbt_packages/
```

---

## Setup Guide

See [SETUP.md](SETUP.md) for full step-by-step instructions covering GCP, Mage, dbt, and VS Code Remote SSH configuration.

## Encountered Errors & Solutions

See [ERRORS.md](ERRORS.md) for troubleshooting notes.
