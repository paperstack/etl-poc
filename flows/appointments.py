from prefect import Parameter, utilities
from prefect.core.flow import Flow
import logging
from tasks.appointment_tasks import extract_nodes, build_graphs, post_graph,\
  aggregate_summaries
from prefect.engine.results.prefect_result import PrefectResult

log = utilities.logging.get_logger()
with Flow("St. Lukes Appointments ETL") as flow:
  input_file_path = Parameter("input_file_path", default="/Users/alex/development/projects/stellar/sfe/fixtures/tests/sample_data/stlukes_appointments/St_Lukes_Sample_Appointments_20201207.txt")
  nodes = extract_nodes(input_file_path)
  graphs = build_graphs(nodes)
  post_summaries = post_graph.map(graphs)
  aggregate_summaries(post_summaries)
  
#flow.run()
flow.register(project_name="PoC")
