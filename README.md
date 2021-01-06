# etl-pushtrain-poc
ETL Pushtrain PoC - This is an experimental repository that implements a prefect flow to load St. Lukes Appointment data.

More details [here](https://www.notion.so/Push-Train-ETL-eb0388d0784846b8b352705b9fd1beb3)

Installation:
Install [Prefect](https://docs.prefect.io/core/getting_started/installation.html)

After following the installation instructions add the file ~/.prefect/config.toml and put in the following contents:

```
[flows]
checkpointing=true
```

When running the server it should be done as follows 
```prefect server start --postgres-port 5433``

By default the Prefect server will start it's own Postgres on port 5432 and that can conflict with the local SFE postgres if it's running on the default port. 5433 can be any port as long is doesnt conflict with a previously running service. 

When starting the prefect agent this project must be on it's PYTHONPATH. To do this invoke the agent thusly:

```
prefect agent start --import-path /path/to/this/project -f
```