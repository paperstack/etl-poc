# etl-pushtrain-poc
ETL Pushtrain PoC - This is an experimental repository that implements a prefect flow to load St. Lukes Appointment data.

More details [here](https://www.notion.so/Push-Train-ETL-eb0388d0784846b8b352705b9fd1beb3)

## Prerequisites
1. You need docker installed
2. Install [Prefect](https://docs.prefect.io/core/getting_started/installation.html)
3. Add the file ~/.prefect/config.toml and put in the following contents:
    ```
    [flows]
    checkpointing=true
    ```
4. Create a virtualenv for the project and install requirements:
    ```
    pyenv virtualenv 3.7.4 stellar_etl_3_7
    pyenv local stellar_etl_3_7
    pip install -r requirements.txt
    ```

## How to run

1. When running the server it should be done as follows:
    ```
    prefect server start --postgres-port 5433
    ```
    By default the Prefect server will start it's own Postgres on port 5432 and that can conflict with the local SFE postgres if it's running on the default port. 5433 can be any port as long is doesnt conflict with a previously running service. 

2. When starting the prefect agent this project must be on it's PYTHONPATH. To do this invoke the agent thusly:
    ```
    prefect agent start --import-path /path/to/this/project -f
    ```

3. Create the Prefect project:
    ```
    prefect create project 'PoC'
    ```

4. Register the Appointments flow:
    ```
    python -m flows.appointments
    ```

The Appointments flow currently takes in two config params:

ge_ctx_root: Absolute path to Great Expectations suite (should be /path/to/repo/great_expectations)

input_file_path: Absolute path to external appointment data