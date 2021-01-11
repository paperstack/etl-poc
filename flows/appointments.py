from prefect import Parameter, utilities
from prefect.core.flow import Flow
import logging
from tasks.appointment_tasks import  build_graphs, post_graph,\
  aggregate_summaries, extract_data_frame, extract_nodes
from prefect.engine.results.prefect_result import PrefectResult
from prefect.tasks.great_expectations.checkpoints import RunGreatExpectationsValidation
from prefect.engine.signals import VALIDATIONFAIL, FAIL
from prefect.triggers import manual_only
from prefect.environments.execution.local import LocalEnvironment
from prefect.run_configs.base import UniversalRun
from prefect.environments.storage.github import GitHub
from prefect.storage.docker import Docker

log = utilities.logging.get_logger()
validation_task = RunGreatExpectationsValidation()

with Flow("St. Lukes Appointments ETL") as flow:
  #input_file_path = Parameter("input_file_path", default="/Users/alex/development/projects/prefect_etl/St_Lukes_Sample_Appointments_20201207.txt")
  #ge_ctx_root = Parameter("ge_ctx_root", default="/Users/alex/development/projects/prefect_etl/great_expectations")

  input_file_path = Parameter("input_file_path", default="/app/10.txt")
  ge_ctx_root = Parameter("ge_ctx_root", default="/app/great_expectations")

  sftp_password = Parameter('sftp_password', default=None)
  sftp_file_path = Parameter('sftp_file_path', default=None)

  df = extract_data_frame(input_file_path, sftp_password, sftp_file_path)
  validation_task(
    batch_kwargs={"dataset": df, "datasource": "appts"},
    expectation_suite_name="STLUKES_DEV_6K_APPTS.warning",
    context_root_dir=ge_ctx_root
                  )
  nodes = extract_nodes(df)
  graphs = build_graphs(nodes)
  post_summaries = post_graph.map(graphs)
  aggregate_summaries(post_summaries)
  
flow.run()
flow.run_config = UniversalRun(labels=["st_lukes"])
#flow.storage = Docker("stellaralex", files={"/Users/alex/development/projects/prefect_etl": "modules/prefect_etl"}, env_vars={"PYTHONPATH": "$PYTHONPATH:modules/prefect_etl"},
#                     python_dependencies=["pandas", "paramiko"])
flow.storage = GitHub(
    repo="paperstack/etl-poc",                 # name of repo
    path="flows/appointments.py"
)

#flow.register(project_name="PoC")
#flow.run_agent(token="Go-8i0PtDRX-PYH24Gz92Q")
