import subprocess

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data(data, *args, **kwargs):
    result = subprocess.run(
        ["/home/zoeyserdyuk/dbt_env/bin/dbt", "run",
         "--profiles-dir", "/home/zoeyserdyuk/dbt_uber_project",
         "--project-dir", "/home/zoeyserdyuk/dbt_uber_project"],
        capture_output=True,
        text=True
    )

    output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
    print(output)

    if result.returncode != 0:
        raise Exception(f"dbt run failed:\n{output}")
    
    return {}
