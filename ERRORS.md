# Errors & Solutions

Troubleshooting log for the Uber Data Engineering Project.

---

## 1. Mage-AI Installation: `externally-managed-environment`

**Error:**
```
error: externally-managed-environment
× This environment is externally managed
```

**Cause:** Python 3.11+ prevents system-wide pip installs to protect OS-level packages on Debian/Ubuntu systems like GCP VMs.

**Solution:** Use a virtual environment instead:
```bash
python3 -m venv ~/.venv
source ~/.venv/bin/activate
pip install mage-ai
```

> Note: `pipx` was attempted but is not suitable for Mage because Mage requires many dependencies (pandas, polars, pyarrow, etc.) that are difficult to manage in pipx's isolated environments.

---

## 2. ImportError: Pandas requires newer version of jinja2

**Error:**
```
ImportError: Pandas requires version '3.1.5' or newer of 'jinja2' (version '3.1.3' currently installed)
```

**Solution:**
```bash
pip install --upgrade pandas jinja2
```

---

## 3. Spark Config Authentication Error

**Error:** Unexpected "Authentication" error in Spark config.

<img width="873" height="676" alt="image" src="https://github.com/user-attachments/assets/985a5346-bdd3-454b-a23d-a4b8d5040f4c" />

**Cause:** Accidentally hardcoded `Authentication: mode: none` in `metadata.yaml` while experimenting with removing the login page.

**Solution:** Remove the hardcoded value from `metadata.yaml`.

---

## 4. SyntaxError: Unexpected character after line continuation

**Error:**
```
SyntaxError: unexpected character after line continuation character
```

**Cause:** Used backslashes `\` for line continuation in SQL/Python.

**Solution:** Wrap the statement in parentheses `()` instead of using backslashes.

---

## 5. Missing Pipeline Files After Restart

**Problem:** After restarting Mage the next day, created files were not visible.

**Cause:** Accidentally created a nested folder `uber_project/uber_project/`, so files were in the wrong location.

**Solution:** Move files to the correct location and delete the empty nested folder:
```bash
mv ~/uber_project/uber_project/transformers/transformer_uber_data.py ~/uber_project/transformers/
```

---

## 6. "Page Unresponsive" When Editing Pipeline

<img width="788" height="456" alt="image" src="https://github.com/user-attachments/assets/988871f7-5f4f-47fc-9dfa-f208a0610756" />

**Error:** Constantly getting "Page Unresponsive" when clicking Edit Pipeline in Mage.

**Cause:** Pipeline appears to be corrupted.

**Solution:** Back up and recreate the project, copying only the code files:
```bash
cp -r uber_project uber_project_backup
rm -rf uber_project
mage init uber_project
cd uber_project
cp ../uber_project_backup/transformers/*.py transformers/
cp ../uber_project_backup/data_loaders/*.py data_loaders/
```

---

## 7. Mage UI Cannot Locate Files

**Problem:** Mage UI couldn't find data loader and transformer files, even though they were visible in the terminal. Clearing cache, refreshing, and restarting Mage did not help.

**Cause:** Suspected Mage UI bug.

**Solution:** Recreate the data loader and transformer blocks manually in the Mage UI.

---

## 8. io_config.yaml Credentials Error

<img width="658" height="172" alt="image" src="https://github.com/user-attachments/assets/43dea727-b0f8-4d8d-ae16-4968c16c52be" />

**Error:** After entering credentials into `io_config.yaml`, getting an authentication error.

**Cause:** Accidentally hardcoded an extra duplicate key `client_x509_cert_url` in the YAML file.

**Solution:** Remove the duplicate key from `io_config.yaml`.

---

## 9. Google Cloud Not Installed on VM

**Error:** Running data exporter fails with a missing Google Cloud library error.

<img width="631" height="444" alt="image" src="https://github.com/user-attachments/assets/d5e59af0-4794-4773-adae-04c319956484" />

**Solution:**
```bash
pip install google-cloud
pip install google-cloud-bigquery
```

---

## 10. Missing `db-dtypes` Dependency

<img width="629" height="533" alt="image" src="https://github.com/user-attachments/assets/660f7ad4-8179-4fff-8e1c-c0a5a28513df" />

**Error:** BigQuery export fails due to missing dependency.

**Cause:** `db-dtypes` handles data type conversions between BigQuery and pandas.

**Solution:**
```bash
pip install db-dtypes
```

---

## 11. Cannot Export Dictionary of DataFrames to BigQuery

**Error:** BigQuery exporter fails when passing a dictionary of DataFrames.

**Cause:** BigQuery's `export()` method only accepts one DataFrame at a time.

**Solution:** Loop through the dictionary and export each DataFrame individually:
```python
for table_name, df in data.items():
    # export df to BigQuery as table_name
```

---

## 12. Git Not Installed on VM

**Error:**
```
Failed to initialize: Bad git executable.
```

**Solution:**
```bash
sudo apt-get install git -y
```
