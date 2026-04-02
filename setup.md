# Setup Guide — Uber Data Engineering Project

---

## 1. Create a GCP Account

Set up a Google Cloud account and create a new project.

---

## 2. Upload Data to Google Cloud Storage

Make the data file publicly accessible:

- Go to your GCS bucket → Permissions → Switch to **fine-grained**
- Set public access on the file

---

## 3. Deploy Mage on GCP Compute Engine

1. Create a VM Instance (E2, 4 cores, 16 GB RAM)
2. SSH into the VM from the GCP Console
3. Create and activate a virtual environment:

```bash
python3 -m venv mage_env
source mage_env/bin/activate
```

4. Install Mage and required packages:

```bash
pip install mage-ai
/home/zoeyserdyuk/mage_env/bin/pip install google-cloud-bigquery
/home/zoeyserdyuk/mage_env/bin/pip install db-dtypes
/home/zoeyserdyuk/mage_env/bin/pip install pandas-gbq
```

5. Create and start your Mage project:

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

## 4. Configure VS Code Remote SSH

Instead of using the GCP Console terminal, you can connect VS Code directly to the VM so you can browse files and edit code like a local project.

### Generate an SSH Key (on your local Windows machine)

```powershell
ssh-keygen -t rsa -b 4096
```

This creates two files in `C:\Users\YourName\.ssh\`:
- `id_rsa` — private key (never share this)
- `id_rsa.pub` — public key (goes on the server)

### Add the Public Key to the VM

1. Copy the contents of `id_rsa.pub`
2. In GCP Console → VM Instance → Edit → **SSH Keys** → Add the key and save

### Prepare the VM's SSH Folder

SSH into the VM from the GCP Console and run:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Then paste your public key into `~/.ssh/authorized_keys`.

### Connect from VS Code

1. Install the **Remote - SSH** extension in VS Code
2. Press `Ctrl+Shift+P` → type `Remote-SSH: Connect to Host`
3. Enter: `zoeyserdyuk@<your-vm-external-ip>`

**How it works:**

| Your Windows Machine (`C:\Users\..\.ssh\`) | Google VM (`~/.ssh/`) |
|---|---|
| `id_rsa` — private key ("the key") | `authorized_keys` — allowed public keys ("the lock") |
| `id_rsa.pub` — public key | |
| `config` — connection settings | |
| `known_hosts` — known servers | |

When you connect, VS Code uses your private key to prove identity, and the VM checks `authorized_keys` for a match. If found, access is granted.

> **Golden rule:** `id_rsa` (private) stays on your machine forever. `id_rsa.pub` (public) goes on every server you want to access.

---

## 5. Configure BigQuery Credentials (for Mage)

1. GCP Console → APIs & Services → Credentials → Create Service Account → Download JSON key
2. Paste the credentials into `io_config.yaml` inside your Mage project

> **Never commit `io_config.yaml`** — add it to `.gitignore`

---

## 6. Install dbt (Separate from Mage)

> **Why separate?** dbt could not be run natively inside Mage due to environment conflicts. It is installed in its own virtual environment and triggered from Mage using Python's `subprocess` module.

### Create a dbt Virtual Environment

```bash
python3 -m venv /home/zoeyserdyuk/dbt_env
source /home/zoeyserdyuk/dbt_env/bin/activate
pip install dbt-bigquery
```

### Create the dbt Project Folder

```bash
mkdir -p /home/zoeyserdyuk/dbt_uber_project
cd /home/zoeyserdyuk/dbt_uber_project
```

### Create the GCP Keys Folder and Upload Service Account Key

```bash
mkdir -p /home/zoeyserdyuk/dbt_uber_project/keys
```

Upload the service account JSON to your GCS bucket, then copy it to the VM:

```bash
gsutil cp gs://os-gcp-bucket/key_uber-data-pipeline-service-account.json \
  /home/zoeyserdyuk/dbt_uber_project/keys/service-account.json
```

To verify the file is there:

```bash
find /home/zoeyserdyuk -name "service-accoun*" 2>/dev/null
```

> **Never commit the key file** — add `keys/` to `.gitignore`

---

## 7. Configure dbt Profiles

The `profiles.yml` file tells dbt how to connect to BigQuery. It is kept **inside the project folder** (not in `~/.dbt/`) because dbt is invoked via `subprocess` with an explicit `--profiles-dir` flag.

Create the file:

```bash
nano /home/zoeyserdyuk/dbt_uber_project/profiles.yml
```

Paste the following (replace values with your own GCP project and dataset IDs):

```yaml
dbt_uber_project:          # must match `profile:` in dbt_project.yml
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: uber-data-pipeline-487320       # GCP project ID
      dataset: ds_uber_project                 # BigQuery dataset ID
      keyfile: /home/zoeyserdyuk/dbt_uber_project/keys/service-account.json
      threads: 4
      timeout_seconds: 300
      location: US                             # or EU depending on your BigQuery region
```

> The profile name `dbt_uber_project` must match exactly what is set under `profile:` in `dbt_project.yml`.

---

## 8. Install dbt Packages

Create `packages.yml` in your dbt project folder:

```bash
nano /home/zoeyserdyuk/dbt_uber_project/packages.yml
```

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.3.0
```

Then install the packages:

```bash
/home/zoeyserdyuk/dbt_env/bin/dbt deps \
  --profiles-dir /home/zoeyserdyuk/dbt_uber_project \
  --project-dir /home/zoeyserdyuk/dbt_uber_project
```

This downloads `dbt_utils` into `dbt_packages/dbt_utils/` automatically.

---

## 9. Create dbt Source Config

Create `models/staging/sources.yml` — this tells dbt where your raw data lives in BigQuery:

```bash
mkdir -p /home/zoeyserdyuk/dbt_uber_project/models/staging
nano /home/zoeyserdyuk/dbt_uber_project/models/staging/sources.yml
```

---

## 10. Running dbt Commands

Always activate dbt's virtual environment first and run from the project root:

```bash
# Activate dbt venv
source /home/zoeyserdyuk/dbt_env/bin/activate

# Navigate to project root
cd /home/zoeyserdyuk/dbt_uber_project

# Run all models
dbt run \
  --profiles-dir /home/zoeyserdyuk/dbt_uber_project \
  --project-dir /home/zoeyserdyuk/dbt_uber_project

# Run only staging models
dbt run --select staging \
  --profiles-dir /home/zoeyserdyuk/dbt_uber_project \
  --project-dir /home/zoeyserdyuk/dbt_uber_project

# Full refresh (rebuilds everything from scratch)
dbt run --full-refresh \
  --profiles-dir /home/zoeyserdyuk/dbt_uber_project \
  --project-dir /home/zoeyserdyuk/dbt_uber_project
```

### Triggering dbt from Mage via subprocess

Because dbt runs in a separate environment, Mage calls it using Python's `subprocess` module:

```python
import subprocess

result = subprocess.run(
    [
        "/home/zoeyserdyuk/dbt_env/bin/dbt",
        "run",
        "--profiles-dir", "/home/zoeyserdyuk/dbt_uber_project",
        "--project-dir", "/home/zoeyserdyuk/dbt_uber_project",
    ],
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.stderr)
```

---

## 11. Version Control

```bash
sudo apt-get install git -y

cd ~/uber_project
git add uber_project/data_loaders/dl_uber_data.py
git add uber_project/transformers/tf_uber_data.py
git add uber_project/pipelines/
git commit -m "uber project pipeline"
git push origin master
```

### Recommended `.gitignore`

```
io_config.yaml
keys/
*.json
dbt_packages/
```

---

## Quick Reference — Common Commands

| Task | Command |
|---|---|
| Activate Mage venv | `source mage_env/bin/activate` |
| Start Mage | `cd ~/uber_project && mage start uber_project` |
| Activate dbt venv | `source /home/zoeyserdyuk/dbt_env/bin/activate` |
| Run dbt | `dbt run --profiles-dir ... --project-dir ...` |
| Install dbt packages | `dbt deps --profiles-dir ... --project-dir ...` |
| Find a file on VM | `find /home/zoeyserdyuk -name "filename*" 2>/dev/null` |
