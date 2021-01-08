from prefect import Parameter, utilities
from prefect.core.flow import Flow
import logging
from tasks.appointment_tasks import  build_graphs, post_graph,\
  aggregate_summaries, extract_data_frame, extract_nodes
from prefect.engine.results.prefect_result import PrefectResult
from prefect.tasks.great_expectations.checkpoints import RunGreatExpectationsValidation

log = utilities.logging.get_logger()
validation_task = RunGreatExpectationsValidation()

with Flow("St. Lukes Appointments ETL") as flow:
  input_file_path = Parameter("input_file_path", default="/Users/alex/development/projects/stellar/sfe/fixtures/tests/sample_data/stlukes_appointments/St_Lukes_Sample_Appointments_20201207.txt")
  ge_ctx_root = Parameter("ge_ctx_root", default="/Users/alex/development/projects/prefect_etl/great_expectations")

  sftp_password = Parameter('sftp_password')
  sftp_file_path = Parameter('sftp_file_path')

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
  
#flow.run()
flow.register(project_name="PoC")
